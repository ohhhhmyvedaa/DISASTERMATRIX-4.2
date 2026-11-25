import os, sys, json, time, uuid
from datetime import datetime, timezone
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from dotenv import load_dotenv
from core.database import save_reading, history, save_chat, get_chat, clear_chat
from core.flood_model import tank_volume_litres, rainfall_volume_litres, water_balance, rate_of_rise, linear_projection
from core.risk_engine import weighted_risk, risk_label
from core.route_optimizer import shortest_route
from core.resource_allocator import allocate_resources
from core.simulation_engine import simulate
from core.serial_handler import SerialReader, available_ports
from core.report_generator import make_pdf
from core.weather_client import fetch_weather
from core.city_intelligence import load_hazard_sources, load_chennai_locations, city_summary, CITY_COORDINATES
from ai.chatbot import respond

load_dotenv()
st.set_page_config(page_title="DISASTERMATRIX 4.0", page_icon="🌊", layout="wide")
st.markdown("""
<style>
.stApp{background:linear-gradient(145deg,#07111f 0%,#0b1728 60%,#101d31 100%);color:#e8f0fb}
[data-testid="stSidebar"]{background:#091525;border-right:1px solid #20334b}
.block-container{padding-top:1.3rem;max-width:1600px}
h1,h2,h3{color:#f2f7ff!important}
div[data-testid="stMetric"]{background:#101f33;border:1px solid #263d59;padding:15px;border-radius:13px}
div[data-testid="stMetricLabel"]{color:#9db3ce}
div[data-testid="stMetricValue"]{color:#f5f9ff}
.dm-card{background:#101f33;border:1px solid #263d59;border-radius:14px;padding:16px;margin-bottom:10px}
.dm-muted{color:#9db3ce;font-size:0.86rem}
.small-pill{display:inline-block;padding:4px 9px;border-radius:20px;background:#183653;color:#9fd0ff;font-size:12px}
</style>
""",unsafe_allow_html=True)

if "serial_reader" not in st.session_state: st.session_state.serial_reader=SerialReader()
if "chat_session" not in st.session_state: st.session_state.chat_session=str(uuid.uuid4())[:8]
if "chat_messages" not in st.session_state: st.session_state.chat_messages=[]

CITY_DATA=Path(__file__).parent/"data"/"city_historical_rainfall.csv"
city_df=pd.read_csv(CITY_DATA)

with st.sidebar:
    st.markdown("## 🌊 DISASTERMATRIX")
    st.caption("4.0  |  DISASTER INTELLIGENCE PLATFORM")
    page=st.radio("NAVIGATION",["Command Centre","City Intelligence","City Hazard Atlas","Flood Mathematics","Risk Map & Routes","Simulation Lab","Resource Allocation","AI Companion","Experiments & Reports","Hardware & Calibration"])
    st.divider()
    city=st.selectbox("CITY PROFILE",["Chennai","Puducherry","Tiruchirappalli"])
    mode=st.radio("OPERATING MODE",["Simulation / Manual","Live Arduino"],index=0)
    st.caption("Educational prototype • Not an official warning system")

st.title("DISASTERMATRIX 4.0")
st.markdown("**The Mathematical Brain of a Disaster-Resilient City**")
st.markdown('<span class="small-pill">AI-ASSISTED ANALYSIS</span> &nbsp; <span class="small-pill">IoT TELEMETRY</span> &nbsp; <span class="small-pill">CITY CLIMATE INTELLIGENCE</span>',unsafe_allow_html=True)
st.caption(f"{city} profile  ·  {datetime.now().strftime('%d %b %Y, %I:%M %p')} IST (device clock)")

# Session state defaults
defaults={"water":6.0,"soil":42.0,"distance":24.0,"water_contact":0,"pump":0,
          "rain":25.0,"tank_len":40.0,"tank_wid":30.0,"tank_h":30.0,
          "weights":[0.4,0.3,0.15,0.15],"experiment":"City resilience trial"}
for k,v in defaults.items():
    if k not in st.session_state: st.session_state[k]=v

def current_payload():
    if mode=="Live Arduino":
        reader=st.session_state.serial_reader
        try:
            msg=reader.read_one()
            if msg:
                st.session_state.water=float(msg["water_level_cm"]) if msg.get("water_level_cm") is not None else None
                st.session_state.soil=float(msg["soil_moisture_pct"]) if msg.get("soil_moisture_pct") is not None else None
                st.session_state.distance=msg.get("distance_cm")
                st.session_state.water_contact=msg.get("water_sensor",0)
                st.session_state.pump=msg.get("pump_status",0)
                return msg
        except Exception as e:
            st.warning(f"Serial read issue: {e}")
    return {"water_level_cm":st.session_state.water,"soil_moisture_pct":st.session_state.soil,
            "distance_cm":st.session_state.distance,"water_sensor":st.session_state.water_contact,
            "pump_status":st.session_state.pump,"valid":True}
payload=current_payload()
water=st.session_state.water if st.session_state.water is not None else 0
soil=st.session_state.soil if st.session_state.soil is not None else 0
depth_pct=min(100,water/max(st.session_state.tank_h,1)*100)
rise_pct=min(100,max(0,water*3))
drain_stress=35.0
risk=weighted_risk(depth_pct,rise_pct,soil,drain_stress,tuple(st.session_state.weights))
label=risk_label(risk)
volume=tank_volume_litres(st.session_state.tank_len,st.session_state.tank_wid,water)
stamp=datetime.now().astimezone().isoformat(timespec="seconds")

if page=="Command Centre":
    st.subheader("Live operations overview")
    a,b,c,d,e=st.columns(5)
    a.metric("Water depth",f"{water:.1f} cm" if payload.get("valid",True) else "Invalid")
    b.metric("Soil moisture",f"{soil:.1f}%")
    c.metric("Experimental risk",f"{risk:.1f}/100",label)
    d.metric("Tank volume",f"{volume:.2f} L")
    e.metric("Pump state","ON" if payload.get("pump_status") else "OFF")
    st.info(f"DATA MODE: {'LIVE HARDWARE' if mode=='Live Arduino' else 'MANUAL / SIMULATION'}  ·  City profile: {city}. City historical data is separate from this tabletop sensor model.")
    left,right=st.columns([1.5,1])
    with left:
        st.markdown("### Water-level telemetry")
        h=history(200)
        if not h.empty and h["water_depth_cm"].notna().any():
            chart=h.dropna(subset=["water_depth_cm"]).sort_values("timestamp")
            st.plotly_chart(px.line(chart,x="timestamp",y="water_depth_cm",title="Saved experimental readings",markers=True),use_container_width=True)
        else:
            st.warning("No saved telemetry yet. Save a reading from Experiments & Reports or connect the Arduino.")
    with right:
        st.markdown("### System assessment")
        st.markdown(f'<div class="dm-card"><h2>{label}</h2><p>Experimental risk index: {risk:.1f}/100</p><p class="dm-muted">Weighted from depth, rise proxy, soil moisture and assumed drainage stress. Not a flood probability.</p></div>',unsafe_allow_html=True)
        st.write("**Secondary water contact:**", "DETECTED" if payload.get("water_sensor") else "NOT DETECTED")
        st.write("**Serial link:**", "Connected" if st.session_state.serial_reader.connection else "Not connected")
        st.write("**Last UI refresh:**",stamp)
    st.markdown("### Quick experiment controls")
    x,y=st.columns(2)
    with x:
        st.session_state.water=st.slider("Manual water depth (cm)",0.0,st.session_state.tank_h,float(water),0.5,disabled=(mode=="Live Arduino"))
        st.session_state.soil=st.slider("Manual soil moisture (%)",0.0,100.0,float(soil),1.0,disabled=(mode=="Live Arduino"))
    with y:
        st.session_state.rain=st.number_input("Manual rainfall input (mm)",0.0,500.0,float(st.session_state.rain),1.0)
        st.session_state.experiment=st.text_input("Experiment name",st.session_state.experiment)
    if st.button("Save current experiment reading",type="primary"):
        save_reading(timestamp=stamp,city=city,water_depth_cm=water,distance_cm=st.session_state.distance,
                     soil_moisture_pct=soil,water_sensor=int(payload.get("water_sensor",0)),
                     pump_status=int(payload.get("pump_status",0)),mode=mode.upper(),risk_score=risk,
                     experiment=st.session_state.experiment,note="Saved from command centre")
        st.success("Reading saved to local SQLite database.")

elif page=="City Intelligence":
    st.subheader("Real-world city climate reference")
    st.warning("Historical published reference data. These are not live rainfall gauges, current flood levels or live warnings.")
    subset=city_df[city_df.city.isin(["Chennai","Puducherry","Tiruchirappalli"])]
    for cty in ["Chennai","Puducherry","Tiruchirappalli"]:
        rows=subset[subset.city==cty]
        with st.expander(cty,expanded=(cty==city)):
            for _,r in rows.iterrows():
                st.metric(f"{r['year']} · {r['period_or_context']}",f"{r['rainfall_mm']} mm")
                st.caption(f"{r['geography']} | {r['source']} | {r['data_type']}")
                st.markdown(f"[Open source document]({r['source_url']})")
    st.markdown("### Compare selected historical reference values")
    latest=subset[subset.year.astype(str).isin(["2021","2022","2023"])]
    st.dataframe(subset[["city","year","rainfall_mm","period_or_context","geography","source"]],use_container_width=True,hide_index=True)
    st.markdown("### Optional current weather context")
    st.caption("Open-Meteo API context is model/API-derived and is not a government rain gauge observation.")
    if st.button(f"Fetch current weather context for {city}"):
        try:
            wx=fetch_weather(city)
            cols=st.columns(4)
            cols[0].metric("Temperature",f"{wx.get('temperature_2m','—')} °C")
            cols[1].metric("Humidity",f"{wx.get('relative_humidity_2m','—')} %")
            cols[2].metric("Precipitation",f"{wx.get('precipitation','—')} mm")
            cols[3].metric("Wind speed",f"{wx.get('wind_speed_10m','—')} km/h")
            st.caption(f"API timestamp: {wx.get('time','not supplied')} · Open-Meteo")
        except Exception as e: st.error(f"Weather API unavailable: {e}")
    st.markdown("### Interpretation")
    st.write("The reporting periods and geographic definitions differ. Use each value with its source and period; do not infer that one city is always safer or wetter than another.")

elif page=="City Hazard Atlas":
    st.subheader("Regional hazard atlas · official planning references")
    st.warning("This atlas combines official historical/planning documents with city-centre locator coordinates. It does not display live flood boundaries, surveyed ward polygons or real-time inundation.")
    atlas = pd.DataFrame([{"City": name, "Latitude": coords["lat"], "Longitude": coords["lon"], "Marker meaning": coords["label"]} for name, coords in CITY_COORDINATES.items()])
    try:
        map_fig = px.scatter_mapbox(atlas, lat="Latitude", lon="Longitude", hover_name="City", hover_data=["Marker meaning"], zoom=5.3, height=460)
        map_fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":10,"l":0,"b":0}, paper_bgcolor="#0b1728", font_color="#e8f0fb")
        st.plotly_chart(map_fig, use_container_width=True)
    except Exception as exc:
        st.info(f"Map view unavailable in this Plotly version: {exc}")
        st.dataframe(atlas, use_container_width=True, hide_index=True)
    summary = city_summary(city)
    st.markdown(f"### {city} · {summary['headline']}")
    st.write(summary["detail"])
    st.caption(summary["caveat"])
    if city == "Chennai":
        roads = load_chennai_locations()
        st.markdown("#### Selected GCC drainage-intervention streets")
        st.caption("Selected entries transcribed from GCC Resolution 089/2021. The original document states that its full list covers 90 roads across 23 locations; this app dataset is a selected subset, not the complete register.")
        st.dataframe(roads[["street_or_location","zone","division_or_ward","documented_context","document_year"]], use_container_width=True, hide_index=True)
    elif city == "Tiruchirappalli":
        st.markdown("#### Historical ward references in the 2024 city action plan")
        st.write("Ward 28 and parts of wards 2, 27, 21, 17, 31, 33, 53, 52 and 30 are named in the plan's urban-flood vulnerability discussion.")
        st.metric("Estimated city area within urban/riverine flood influence", "21%", help="Planning assessment reported in the 2024 city action plan; not a current measurement.")
        st.metric("Estimated affected population in that assessment", "0.23 million", help="Planning assessment reported in the 2024 city action plan; not a current measurement.")
    else:
        st.markdown("#### Published regional flood-hazard classes")
        st.dataframe(pd.DataFrame({"Class": ["Low","Medium","High","Very high"], "Modelled inundation depth": ["< 1 m","1–2 m","2–3 m","> 3 m"]}), use_container_width=True, hide_index=True)
        st.write("The cited plan describes Oulgaret and Puducherry municipalities as flood-prone in its regional assessment.")
    st.markdown("#### Official source library")
    srcs=load_hazard_sources()
    for _, row in srcs[srcs.city==city].iterrows():
        with st.expander(row["document_title"]):
            st.write(row["documented_finding"])
            st.caption(row["interpretation_limit"])
            st.markdown(f"[Open official document]({row['source_url']})")
    st.markdown("#### Official rainfall and warning data gateways")
    st.markdown("""- [IMD API documentation and data catalogue](https://api.imd.gov.in/public/api_reference.html) — district rainfall, current weather, warnings and forecast API descriptions. API access may require registration/credentials.
- [National Water Data Portal — daily IMD rainfall dataset](https://nwdp.nwic.gov.in/en/dataset/rainfall-daily-imd) — district-wise and state-wise observed rainfall CSV resources.
- [Open Government Data rainfall catalogue](https://data.gov.in/catalog/rainfall) — daily district-wise rainfall resources.""")
    st.caption("The current-weather button in City Intelligence uses Open-Meteo context. For official operational monitoring, consult IMD and local administration portals directly.")

elif page=="Flood Mathematics":
    st.subheader("Transparent flood mathematics engine")
    c1,c2,c3=st.columns(3)
    with c1: st.session_state.tank_len=st.number_input("Tank length (cm)",1.0,500.0,float(st.session_state.tank_len))
    with c2: st.session_state.tank_wid=st.number_input("Tank width (cm)",1.0,500.0,float(st.session_state.tank_wid))
    with c3: st.session_state.tank_h=st.number_input("Reference height (cm)",1.0,500.0,float(st.session_state.tank_h))
    depth=st.number_input("Water depth (cm)",0.0,float(st.session_state.tank_h),float(min(water,st.session_state.tank_h)))
    st.latex(r"V_{L}=\\frac{L_{cm}\\times W_{cm}\\times h_{cm}}{1000}")
    st.metric("Calculated tank water volume",f"{tank_volume_litres(st.session_state.tank_len,st.session_state.tank_wid,depth):.3f} L")
    st.latex(r"V_{rain}(L)=P(mm)\\times A(m^2)")
    p=st.number_input("Rainfall depth (mm)",0.0,1000.0,float(st.session_state.rain))
    area=st.number_input("Collection area (m²)",0.1,10000.0,10.0)
    st.metric("Rainfall volume equivalent",f"{rainfall_volume_litres(p,area):.2f} L")
    st.markdown("### Water balance")
    i1,i2,i3=st.columns(3)
    inflow=i1.number_input("Inflow (L)",0.0,100000.0,20.0)
    drainage=i2.number_input("Drainage outflow (L)",0.0,100000.0,5.0)
    infiltration=i3.number_input("Infiltration (L)",0.0,100000.0,3.0)
    st.metric("Change in storage",f"{water_balance(inflow,drainage,infiltration):.2f} L")
    st.caption("Δstorage = inflow − drainage − infiltration. A negative result means modelled storage decreases.")
    st.markdown("### Experimental risk score weights")
    labels=["Water depth","Rate of rise","Soil moisture","Drainage stress"]
    weights=[]
    for idx,name in enumerate(labels):
        weights.append(st.slider(f"{name} weight",0,100,int(st.session_state.weights[idx]*100),5,key=f"w{idx}"))
    if sum(weights)>0: st.session_state.weights=[v/sum(weights) for v in weights]
    st.write("Normalised weights:",{k:round(v,3) for k,v in zip(labels,st.session_state.weights)})
    st.metric("Experimental flood-risk index",f"{risk:.2f}/100",label)
    st.caption("Index = Σ(normalised component × normalised weight). This is not probability or an official forecast.")
    st.markdown("### Rate of rise and short trend estimate")
    previous=st.number_input("Previous level (cm)",0.0,500.0,max(0.0,water-1))
    elapsed=st.number_input("Elapsed time (seconds)",1.0,86400.0,60.0)
    rr=rate_of_rise(water,previous,elapsed)
    st.metric("Rate of rise",f"{rr:.2f} cm/min" if rr is not None else "Unavailable")
    hist=history(20)
    if len(hist)>=3 and hist.water_depth_cm.notna().sum()>=3:
        pred=linear_projection(hist.sort_values("timestamp").water_depth_cm.dropna().tail(10).tolist(),5)
        st.metric("5-step trend estimate",f"{pred:.2f} cm")
    else: st.info("Save at least three valid readings to enable a simple trend estimate.")
    st.caption("Trend extrapolation is a teaching estimate from recent samples, not a flood forecast.")

elif page=="Risk Map & Routes":
    st.subheader("Educational 4×4 city grid and route laboratory")
    st.caption("The grid is illustrative. It is not a surveyed map of Chennai, Puducherry or Trichy.")
    zones=["Residential A","School","Hospital","Market","Residential B","Main Road","Fire Station","Drainage","Residential C","Police","Shelter 1","Canal","Residential D","Bus Hub","Shelter 2","Lake"]
    grid=pd.DataFrame({"Zone":zones,"Risk":[round(min(100,risk+i*3.4),1) for i in range(16)]})
    grid["Status"]=grid.Risk.apply(risk_label)
    grid["Row"]=[i//4 for i in range(16)]; grid["Col"]=[i%4 for i in range(16)]
    fig=px.scatter(grid,x="Col",y="Row",color="Risk",size=[22]*16,text="Zone",
                   color_continuous_scale=["#2ecc71","#f1c40f","#e67e22","#e74c3c"],range_color=(0,100))
    fig.update_traces(textposition="bottom center")
    fig.update_yaxes(autorange="reversed",dtick=1,showgrid=True)
    fig.update_xaxes(dtick=1,showgrid=True)
    fig.update_layout(height=500,plot_bgcolor="#0b1728",paper_bgcolor="#0b1728",font_color="#e8f0fb")
    st.plotly_chart(fig,use_container_width=True)
    chosen=st.selectbox("Inspect zone",zones)
    zi=zones.index(chosen)
    st.write({"zone":chosen,"experimental_risk":grid.iloc[zi].Risk,"label":grid.iloc[zi].Status,
              "depth_cm":round(water+zi*0.2,1),"vulnerability_score":min(100,35+zi*3)})
    st.markdown("### Dijkstra route demonstration")
    node_names=list("ABCDEFGHIJKLMNOP")
    start=st.selectbox("Start node",node_names,index=0)
    dest=st.selectbox("Destination / shelter node",node_names,index=15)
    penalty=st.slider("Flood-adjusted road cost multiplier",1.0,5.0,1.8,0.1)
    block=st.multiselect("Block roads (edge pairs)",["A-B","B-C","C-D","E-F","F-G","G-H","A-E","E-I","I-M","M-N","N-O","O-P"])
    blocked=[tuple(x.split("-")) for x in block]
    normal=shortest_route(start,dest,blocked_edges=[])
    adjusted=shortest_route(start,dest,blocked_edges=blocked,flood_penalty=penalty)
    a,b=st.columns(2)
    a.write("**Baseline route**"); a.write(normal if normal["path"] else "No path")
    b.write("**Flood-adjusted route**"); b.write(adjusted if adjusted["path"] else "NO SAFE ROUTE IN THIS DEMO GRAPH")
    st.caption("Edge costs are illustrative travel-time units. This is not a real evacuation recommendation.")

elif page=="Simulation Lab":
    st.subheader("Disaster simulation laboratory")
    scenario=st.selectbox("Scenario",["Urban flooding","Heavy rainfall","Drainage blockage","Soil saturation","Earthquake vibration demo","Cyclone scenario","Wildfire scenario"])
    rain=st.slider("Simulated rainfall input (mm)",0,300,60)
    drain=st.slider("Drainage efficiency assumption",0.0,1.0,0.6,0.05)
    saturation=st.slider("Soil saturation assumption (%)",0,100,70)
    start=st.slider("Starting water depth (cm)",0.0,30.0,4.0,0.5)
    if st.button("Run simulation",type="primary"):
        result=simulate(scenario,rain,drain,saturation,start)
        st.success(result["label"])
        st.json(result)
        st.metric("Simulated ending depth",f"{result['end_depth_cm']} cm",f"+{result['delta_depth_cm']} cm")
        st.caption("Scenario outputs are generated by a simplified teaching model and are not measured city conditions.")

elif page=="Resource Allocation":
    st.subheader("Educational resource allocation")
    teams=st.number_input("Rescue teams available (model input)",0,1000,8)
    vehicles=st.number_input("Vehicles available (model input)",0,1000,5)
    kits=st.number_input("Relief kits available (model input)",0,100000,500)
    zones_in=[]
    for z,aff,pri in [("Residential A",120,3),("Market",80,2),("School",60,4),("Low-lying block",150,5)]:
        with st.expander(z):
            affected=st.number_input(f"Population affected · {z}",0,100000,aff,key=f"aff{z}")
            priority=st.slider(f"Priority · {z}",1,5,pri,key=f"pri{z}")
        zones_in.append({"zone":z,"affected":affected,"priority":priority})
    alloc=allocate_resources(zones_in,int(teams),int(vehicles),int(kits))
    st.dataframe(pd.DataFrame(alloc),use_container_width=True,hide_index=True)
    st.caption("This is a proportional classroom allocation exercise, not an operational emergency plan.")

elif page=="AI Companion":
    st.subheader("DISASTERMATRIX AI Companion")
    st.caption("Project-aware educational assistant • Offline answers always available • Optional online LLM")
    ctx={"city":city,"mode":mode,"water_depth_cm":water,"soil_moisture_pct":soil,
         "experimental_risk_index":risk,"risk_label":label,"city_hazard_summary":city_summary(city)}
    st.markdown('<div class="dm-card"><b>Welcome to DISASTERMATRIX AI</b><br><span class="dm-muted">Ask about the sensor readings, historical city data, equations, routes or simulations.</span></div>',unsafe_allow_html=True)
    for m in st.session_state.chat_messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    question=st.chat_input("Ask your project assistant…")
    if question:
        st.session_state.chat_messages.append({"role":"user","content":question})
        with st.chat_message("user"): st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Analysing project context…"):
                answer=respond(question,ctx)
                st.markdown(answer)
        st.session_state.chat_messages.append({"role":"assistant","content":answer})
        save_chat(st.session_state.chat_session,"user",question,datetime.now().isoformat())
        save_chat(st.session_state.chat_session,"assistant",answer,datetime.now().isoformat())
    c1,c2=st.columns(2)
    if c1.button("New chat"):
        st.session_state.chat_session=str(uuid.uuid4())[:8]; st.session_state.chat_messages=[]; st.rerun()
    if c2.button("Clear current chat"):
        clear_chat(st.session_state.chat_session); st.session_state.chat_messages=[]; st.rerun()
    st.caption("Online mode uses OPENAI_API_KEY from .env. Offline fallback does not require an API key.")

elif page=="Experiments & Reports":
    st.subheader("Experiment archive and research reports")
    hist=history(2000)
    if hist.empty: st.info("No experiment readings saved yet. Save a reading from Command Centre.")
    else:
        st.dataframe(hist,use_container_width=True,hide_index=True)
        st.download_button("Export readings as CSV",hist.to_csv(index=False).encode("utf-8"),
                           file_name="disastermatrix_experiments.csv",mime="text/csv")
        latest=hist.iloc[0]
        pdf=make_pdf("DISASTERMATRIX 4.0 — Experiment Report",
                     [("City",latest.city),("Timestamp",latest.timestamp),("Mode",latest.mode),
                      ("Water depth cm",latest.water_depth_cm),("Soil moisture %",latest.soil_moisture_pct),
                      ("Risk index",latest.risk_score),("Experiment",latest.experiment)])
        st.download_button("Generate PDF report",pdf,file_name="disastermatrix_report.pdf",mime="application/pdf")
        st.markdown("### Research note")
        st.write("MAE = mean(|predicted − observed|). Record predictions and later measurements consistently before interpreting model error. A small number of trials cannot establish real-world accuracy.")

elif page=="Hardware & Calibration":
    st.subheader("Hardware connection and calibration")
    ports=available_ports()
    st.write("Detected serial ports:",ports if ports else "No ports detected (or pyserial unavailable).")
    port=st.selectbox("COM port",ports if ports else ["COM3"])
    baud=st.selectbox("Baud rate",[9600,19200,38400,57600,115200],index=0)
    a,b=st.columns(2)
    if a.button("Connect Arduino"):
        try:
            st.session_state.serial_reader.connect(port,baud); st.success(f"Connected to {port}")
        except Exception as e: st.error(f"Connection failed: {e}")
    if b.button("Disconnect"):
        st.session_state.serial_reader.disconnect(); st.info("Serial disconnected.")
    st.markdown("### Calibration values")
    st.session_state.tank_h=st.number_input("Empty tank reference height (cm)",1.0,500.0,float(st.session_state.tank_h))
    dry=st.number_input("Soil dry ADC calibration",0,1023,800)
    wet=st.number_input("Soil wet ADC calibration",0,1023,350)
    if dry==wet: st.error("Dry and wet ADC calibration values must differ.")
    st.number_input("Secondary water sensor digital threshold (document module polarity)",0,1,1)
    st.number_input("Pump maximum runtime (seconds) — Arduino sketch setting",1,120,15)
    st.info("Pump control remains on Arduino. The Python dashboard and AI must never directly switch the pump.")
    st.markdown("### Pin map")
    st.table(pd.DataFrame([
        ["HC-SR04 TRIG","D8"],["HC-SR04 ECHO","D9"],["Soil sensor AO","A0"],
        ["Water sensor DO","D2"],["LCD SDA / SCL","A4 / A5"],
        ["Buzzer","D6"],["MOSFET driver signal","D5"]],columns=["Component","Uno pin"]))
    st.caption("Verify LCD address and water sensor polarity for your exact purchased modules before powering the circuit.")

st.divider()
st.caption("DISASTERMATRIX 4.0 • Educational research prototype • Historical references are attributed • No certified alerts or real-world emergency routing.")
