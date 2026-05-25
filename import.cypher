// ============================================================================
// 船舶故障诊断知识图谱 v4.0 - Neo4j 导入脚本
// 使用: cypher-shell -u neo4j -p 密码 -f import.cypher
// 节点: Symptom/Cause/Step/Equipment/SparePart/Tool/Precaution (7类)
// 关系: CAUSED_BY/FIXED_BY/NEXT_STEP/BELONGS_TO/USES_SPAREPART/REQUIRES_TOOL/HAS_PRECAUTION
// ============================================================================

// ==================== 一、设备 (Level 2 根) ====================
MERGE (e_app:Equipment {uid: 'E_APPLIANCE'}) SET e_app.name='船舶电器', e_app.level=2
MERGE (e_motor:Equipment {uid: 'E_MOTOR_CAT'}) SET e_motor.name='船用电机', e_motor.level=2
MERGE (e_aux:Equipment {uid: 'E_AUXILIARY'}) SET e_aux.name='船舶辅机电气系统', e_aux.level=2
MERGE (e_alarm:Equipment {uid: 'E_ALARM_CAT'}) SET e_alarm.name='船舶报警装置', e_alarm.level=2
MERGE (e_power:Equipment {uid: 'E_POWER_LIFE'}) SET e_power.name='船舶电站与生活设备', e_power.level=2

// Level 3
MERGE (e_cont:Equipment {uid: 'E_CONTACTOR'}) SET e_cont.name='接触器', e_cont.level=3, e_cont.source_page='第四章第二节' MERGE (e_cont)-[:SUBCLASS_OF]->(e_app)
MERGE (e_therm:Equipment {uid: 'E_THERMAL_RELAY'}) SET e_therm.name='热继电器', e_therm.level=3, e_therm.source_page='第四章第三节' MERGE (e_therm)-[:SUBCLASS_OF]->(e_app)
MERGE (e_break:Equipment {uid: 'E_BREAKER'}) SET e_break.name='断路器', e_break.level=3, e_break.source_page='第四章第四节' MERGE (e_break)-[:SUBCLASS_OF]->(e_app)
MERGE (e_plc:Equipment {uid: 'E_PLC'}) SET e_plc.name='PLC', e_plc.level=3, e_plc.source_page='第四章第六节' MERGE (e_plc)-[:SUBCLASS_OF]->(e_app)
MERGE (e_async:Equipment {uid: 'E_ASYNCH_MOTOR'}) SET e_async.name='三相异步电动机', e_async.level=3, e_async.source_page='第五章第三节' MERGE (e_async)-[:SUBCLASS_OF]->(e_motor)
MERGE (e_dc:Equipment {uid: 'E_DC_MOTOR'}) SET e_dc.name='直流电机', e_dc.level=3, e_dc.source_page='第五章第四节' MERGE (e_dc)-[:SUBCLASS_OF]->(e_motor)
MERGE (e_trans:Equipment {uid: 'E_TRANSFORMER'}) SET e_trans.name='船用变压器', e_trans.level=3, e_trans.source_page='第五章第六节' MERGE (e_trans)-[:SUBCLASS_OF]->(e_motor)
MERGE (e_winch:Equipment {uid: 'E_WINCH'}) SET e_winch.name='起货机电气系统', e_winch.level=3, e_winch.source_page='第六章第四节' MERGE (e_winch)-[:SUBCLASS_OF]->(e_aux)
MERGE (e_anchor:Equipment {uid: 'E_ANCHOR'}) SET e_anchor.name='锚机/绞缆机', e_anchor.level=3, e_anchor.source_page='第六章第五节' MERGE (e_anchor)-[:SUBCLASS_OF]->(e_aux)
MERGE (e_steer:Equipment {uid: 'E_STEER'}) SET e_steer.name='舵机电气系统', e_steer.level=3, e_steer.source_page='第六章第六节' MERGE (e_steer)-[:SUBCLASS_OF]->(e_aux)
MERGE (e_boiler:Equipment {uid: 'E_BOILER'}) SET e_boiler.name='辅锅炉电气控制', e_boiler.level=3, e_boiler.source_page='第六章第七节' MERGE (e_boiler)-[:SUBCLASS_OF]->(e_aux)
MERGE (e_fire:Equipment {uid: 'E_FIRE_ALARM'}) SET e_fire.name='火灾报警装置', e_fire.level=3, e_fire.source_page='第七章第二节' MERGE (e_fire)-[:SUBCLASS_OF]->(e_alarm)
MERGE (e_monitor:Equipment {uid: 'E_MONITOR'}) SET e_monitor.name='机舱监测系统', e_monitor.level=3, e_monitor.source_page='第七章第四节' MERGE (e_monitor)-[:SUBCLASS_OF]->(e_alarm)
MERGE (e_gen:Equipment {uid: 'E_GENERATOR'}) SET e_gen.name='发电机及励磁', e_gen.level=3, e_gen.source_page='第一章第三节;第十一章第二节' MERGE (e_gen)-[:SUBCLASS_OF]->(e_power)
MERGE (e_pdist:Equipment {uid: 'E_PDIST'}) SET e_pdist.name='配电装置', e_pdist.level=3, e_pdist.source_page='第十一章第三节' MERGE (e_pdist)-[:SUBCLASS_OF]->(e_power)

// 公共 source 属性
MATCH (e:Equipment) WHERE e.source_doc IS NULL SET e.source_doc='船舶电气设备维护与修理', e.source_author='马昭胜主编', e.source_publisher='机械工业出版社2020', e.created_at=timestamp()

// ==================== 二、接触器 ====================

// --- 共享 Cause ---
MERGE (c_voltage_low:Cause {uid: 'C_VOLTAGE_LOW'}) SET c_voltage_low.name='电源电压过低或波动大', c_voltage_low.check_method='measure', c_voltage_low.check_time='1分钟', c_voltage_low.requires_shutdown=false, c_voltage_low.failure_rate=0.15, c_voltage_low.created_at=timestamp()
MERGE (c_coil_short:Cause {uid: 'C_COIL_SHORT'}) SET c_coil_short.name='线圈内部短路', c_coil_short.check_method='measure', c_coil_short.check_time='3分钟', c_coil_short.requires_shutdown=true, c_coil_short.created_at=timestamp()
MERGE (c_mech_stuck:Cause {uid: 'C_MECH_STUCK'}) SET c_mech_stuck.name='运动部分卡阻/弹簧反力过大/转轴锈蚀', c_mech_stuck.check_method='visual', c_mech_stuck.check_time='2分钟', c_mech_stuck.requires_shutdown=true, c_mech_stuck.failure_rate=0.20, c_mech_stuck.created_at=timestamp()
MERGE (c_short_ring:Cause {uid: 'C_SHORT_RING'}) SET c_short_ring.name='短路环断裂或脱落', c_short_ring.check_method='visual', c_short_ring.check_time='2分钟', c_short_ring.requires_shutdown=true, c_short_ring.failure_rate=0.12, c_short_ring.created_at=timestamp()
MERGE (c_over_freq:Cause {uid: 'C_OVER_FREQ'}) SET c_over_freq.name='操作频率过高或过载使用', c_over_freq.check_method='measure', c_over_freq.check_time='5分钟', c_over_freq.requires_shutdown=false, c_over_freq.created_at=timestamp()

// --- Symptoms ---
MERGE (s_c01:Symptom {uid: 'S_CONT_01'}) SET s_c01.name='吸不上或吸力不足(嗡鸣)', s_c01.primary_features=['吸力不足','嗡鸣','吸不上'], s_c01.sensory_type=['auditory','tactile'], s_c01.source_page='第四章第二节', s_c01.source_table='表4-2', s_c01.created_at=timestamp() MERGE (s_c01)-[:BELONGS_TO]->(e_cont)
MERGE (s_c03:Symptom {uid: 'S_CONT_03'}) SET s_c03.name='不释放或释放缓慢', s_c03.source_page='第四章第二节', s_c03.created_at=timestamp() MERGE (s_c03)-[:BELONGS_TO]->(e_cont)
MERGE (s_c04:Symptom {uid: 'S_CONT_04'}) SET s_c04.name='线圈过热或烧损', s_c04.primary_features=['过热','烧损','冒烟'], s_c04.sensory_type=['visual','olfactory'], s_c04.source_page='第四章第二节', s_c04.created_at=timestamp() MERGE (s_c04)-[:BELONGS_TO]->(e_cont)
MERGE (s_c05:Symptom {uid: 'S_CONT_05'}) SET s_c05.name='交流电磁铁噪声大', s_c05.primary_features=['噪声','嗡鸣','振动'], s_c05.sensory_type=['auditory','tactile'], s_c05.source_page='第四章第二节', s_c05.created_at=timestamp() MERGE (s_c05)-[:BELONGS_TO]->(e_cont)
MERGE (s_c06:Symptom {uid: 'S_CONT_06'}) SET s_c06.name='触头熔焊', s_c06.source_page='第四章第二节', s_c06.created_at=timestamp() MERGE (s_c06)-[:BELONGS_TO]->(e_cont)
MERGE (s_c07:Symptom {uid: 'S_CONT_07'}) SET s_c07.name='触头过热或灼伤', s_c07.primary_features=['过热','灼伤'], s_c07.sensory_type=['visual','tactile'], s_c07.source_page='第四章第二节', s_c07.created_at=timestamp() MERGE (s_c07)-[:BELONGS_TO]->(e_cont)
MERGE (s_c08:Symptom {uid: 'S_CONT_08'}) SET s_c08.name='触头过度磨损', s_c08.source_page='第四章第二节', s_c08.created_at=timestamp() MERGE (s_c08)-[:BELONGS_TO]->(e_cont)

// --- S_C01 CAUSED_BY ---
MERGE (s_c01)-[r_c01a:CAUSED_BY]->(c_voltage_low) SET r_c01a.priority=1, r_c01a.context='线圈电压低于85%UN时吸力不足'
MERGE (c_c01b:Cause {uid: 'C_CONT_01b'}) SET c_c01b.name='操作电源容量不足', c_c01b.check_method='measure', c_c01b.check_time='2分钟', c_c01b.created_at=timestamp() MERGE (s_c01)-[r_c01b:CAUSED_BY]->(c_c01b) SET r_c01b.priority=2
MERGE (s_c01)-[r_c01c:CAUSED_BY]->(c_coil_short) SET r_c01c.priority=3
MERGE (s_c01)-[r_c01d:CAUSED_BY]->(c_mech_stuck) SET r_c01d.priority=4
MERGE (c_c01e:Cause {uid: 'C_CONT_01e'}) SET c_c01e.name='线圈额定电压高于线路电压', c_c01e.check_method='visual', c_c01e.check_time='1分钟', c_c01e.created_at=timestamp() MERGE (s_c01)-[r_c01e:CAUSED_BY]->(c_c01e) SET r_c01e.priority=5
MERGE (c_c01f:Cause {uid: 'C_CONT_01f'}) SET c_c01f.name='触头开距(衔铁气隙)太大', c_c01f.check_method='measure', c_c01f.check_time='2分钟', c_c01f.created_at=timestamp() MERGE (s_c01)-[r_c01f:CAUSED_BY]->(c_c01f) SET r_c01f.priority=6

// --- S_C03 CAUSED_BY ---
MERGE (c_c03a:Cause {uid: 'C_CONT_03a'}) SET c_c03a.name='衔铁反力弹簧失效或缺损', c_c03a.check_method='visual', c_c03a.check_time='2分钟', c_c03a.created_at=timestamp() MERGE (s_c03)-[r_c03a:CAUSED_BY]->(c_c03a) SET r_c03a.priority=1
MERGE (c_c03b:Cause {uid: 'C_CONT_03b'}) SET c_c03b.name='触头熔焊', c_c03b.check_method='visual', c_c03b.check_time='2分钟', c_c03b.failure_rate=0.10, c_c03b.created_at=timestamp() MERGE (s_c03)-[r_c03b:CAUSED_BY]->(c_c03b) SET r_c03b.priority=2
MERGE (s_c03)-[r_c03c:CAUSED_BY]->(c_mech_stuck) SET r_c03c.priority=3
MERGE (c_c03d:Cause {uid: 'C_CONT_03d'}) SET c_c03d.name='铁心极面有油泥黏着', c_c03d.check_method='visual', c_c03d.check_time='1分钟', c_c03d.created_at=timestamp() MERGE (s_c03)-[r_c03d:CAUSED_BY]->(c_c03d) SET r_c03d.priority=4

// --- S_C04 CAUSED_BY ---
MERGE (c_c04a:Cause {uid: 'C_CONT_04a'}) SET c_c04a.name='电源电压过高(>1.1UN)或过低(<0.85UN)', c_c04a.check_method='measure', c_c04a.check_time='1分钟', c_c04a.failure_rate=0.15, c_c04a.created_at=timestamp() MERGE (s_c04)-[r_c04a:CAUSED_BY]->(c_c04a) SET r_c04a.priority=1
MERGE (c_c04b:Cause {uid: 'C_CONT_04b'}) SET c_c04b.name='线圈参数与实际条件不符', c_c04b.check_method='visual', c_c04b.check_time='2分钟', c_c04b.created_at=timestamp() MERGE (s_c04)-[r_c04b:CAUSED_BY]->(c_c04b) SET r_c04b.priority=2
MERGE (s_c04)-[r_c04c:CAUSED_BY]->(c_coil_short) SET r_c04c.priority=3
MERGE (s_c04)-[r_c04d:CAUSED_BY]->(c_over_freq) SET r_c04d.priority=4
MERGE (c_c04e:Cause {uid: 'C_CONT_04e'}) SET c_c04e.name='环境潮湿/腐蚀/高温', c_c04e.check_method='visual', c_c04e.check_time='1分钟', c_c04e.created_at=timestamp() MERGE (s_c04)-[r_c04e:CAUSED_BY]->(c_c04e) SET r_c04e.priority=5
MERGE (s_c04)-[r_c04f:CAUSED_BY]->(c_mech_stuck) SET r_c04f.priority=6, r_c04f.context='卡阻致线圈长时通电'

// --- S_C05 CAUSED_BY ---
MERGE (s_c05)-[r_c05a:CAUSED_BY]->(c_voltage_low) SET r_c05a.priority=1, r_c05a.context='电压低铁心吸合不平产生振动噪声'
MERGE (c_c05b:Cause {uid: 'C_CONT_05b'}) SET c_c05b.name='触头弹簧压力过大或超程过大', c_c05b.check_method='measure', c_c05b.check_time='3分钟', c_c05b.created_at=timestamp() MERGE (s_c05)-[r_c05b:CAUSED_BY]->(c_c05b) SET r_c05b.priority=2
MERGE (c_c05c:Cause {uid: 'C_CONT_05c'}) SET c_c05c.name='衔铁歪斜或机械卡阻', c_c05c.check_method='visual', c_c05c.check_time='2分钟', c_c05c.created_at=timestamp() MERGE (s_c05)-[r_c05c:CAUSED_BY]->(c_c05c) SET r_c05c.priority=3
MERGE (c_c05d:Cause {uid: 'C_CONT_05d'}) SET c_c05d.name='铁心极面有异物或接触不良', c_c05d.check_method='visual', c_c05d.check_time='1分钟', c_c05d.created_at=timestamp() MERGE (s_c05)-[r_c05d:CAUSED_BY]->(c_c05d) SET r_c05d.priority=4
MERGE (s_c05)-[r_c05e:CAUSED_BY]->(c_short_ring) SET r_c05e.priority=5

// --- S_C06~C08 (简化) ---
MERGE (c_c06a:Cause {uid: 'C_CONT_06a'}) SET c_c06a.name='触头容量过小/负载短路/吸力不足/烧损/弹簧小/过频', c_c06a.check_method='visual', c_c06a.check_time='2分钟', c_c06a.created_at=timestamp() MERGE (s_c06)-[r_c06a:CAUSED_BY]->(c_c06a) SET r_c06a.priority=1
MERGE (c_c07a:Cause {uid: 'C_CONT_07a'}) SET c_c07a.name='触头弹簧不足/接触不良/磨损>1/3/过频电流大/高温密闭', c_c07a.check_method='visual', c_c07a.check_time='2分钟', c_c07a.created_at=timestamp() MERGE (s_c07)-[r_c07a:CAUSED_BY]->(c_c07a) SET r_c07a.priority=1
MERGE (c_c08a:Cause {uid: 'C_CONT_08a'}) SET c_c08a.name='操作过频电流大/三相不同步/负载短路', c_c08a.check_method='visual', c_c08a.check_time='2分钟', c_c08a.created_at=timestamp() MERGE (s_c08)-[r_c08a:CAUSED_BY]->(c_c08a) SET r_c08a.priority=1

// --- 接触器 Step (所有单步) ---
MERGE (st_c01a:Step {uid: 'ST_C01A'}) SET st_c01a.name='检测电压' MERGE (c_voltage_low)-[:FIXED_BY]->(st_c01a)
MERGE (st_c01b:Step {uid: 'ST_C01B'}) SET st_c01b.name='更换操作电源' MERGE (c_c01b)-[:FIXED_BY]->(st_c01b)
MERGE (st_c01c:Step {uid: 'ST_C01C'}) SET st_c01c.name='更换线圈' MERGE (c_coil_short)-[:FIXED_BY]->(st_c01c)
MERGE (st_c01d:Step {uid: 'ST_C01D'}) SET st_c01d.name='卸灭弧罩查衔铁去锈加油校正' MERGE (c_mech_stuck)-[:FIXED_BY]->(st_c01d)
MERGE (st_c01e:Step {uid: 'ST_C01E'}) SET st_c01e.name='换匹配电压线圈' MERGE (c_c01e)-[:FIXED_BY]->(st_c01e)
MERGE (st_c01f:Step {uid: 'ST_C01F'}) SET st_c01f.name='调整衔铁气隙' MERGE (c_c01f)-[:FIXED_BY]->(st_c01f)
MERGE (st_c03a:Step {uid: 'ST_C03A'}) SET st_c03a.name='更换或调整反力弹簧' MERGE (c_c03a)-[:FIXED_BY]->(st_c03a)
MERGE (st_c03b:Step {uid: 'ST_C03B'}) SET st_c03b.name='修整或换触头,常熔焊换大一级' MERGE (c_c03b)-[:FIXED_BY]->(st_c03b)
MERGE (st_c03c:Step {uid: 'ST_C03C'}) SET st_c03c.name='去锈加油校正变形' MERGE (c_mech_stuck)-[:FIXED_BY]->(st_c03c)
MERGE (st_c03d:Step {uid: 'ST_C03D'}) SET st_c03d.name='清除铁心极面油泥' MERGE (c_c03d)-[:FIXED_BY]->(st_c03d)
MERGE (st_c04a:Step {uid: 'ST_C04A'}) SET st_c04a.name='调整电源电压' MERGE (c_c04a)-[:FIXED_BY]->(st_c04a)
MERGE (st_c04b:Step {uid: 'ST_C04B'}) SET st_c04b.name='核对铭牌换匹配线圈' MERGE (c_c04b)-[:FIXED_BY]->(st_c04b)
MERGE (st_c04c:Step {uid: 'ST_C04C'}) SET st_c04c.name='电阻比较法判定后换线圈' MERGE (c_coil_short)-[:FIXED_BY]->(st_c04c)
MERGE (st_c04d:Step {uid: 'ST_C04D'}) SET st_c04d.name='换大一级电流接触器' MERGE (c_over_freq)-[:FIXED_BY]->(st_c04d)
MERGE (st_c04e:Step {uid: 'ST_C04E'}) SET st_c04e.name='换防水IP56或耐高温F级' MERGE (c_c04e)-[:FIXED_BY]->(st_c04e)
MERGE (st_c04f:Step {uid: 'ST_C04F'}) SET st_c04f.name='去锈加油校正复位弹簧' MERGE (c_mech_stuck)-[:FIXED_BY]->(st_c04f)
MERGE (st_c05a:Step {uid: 'ST_C05A'}) SET st_c05a.name='调整电源电压至85%~110%UN' MERGE (c_voltage_low)-[:FIXED_BY]->(st_c05a)
MERGE (st_c05b:Step {uid: 'ST_C05B'}) SET st_c05b.name='调整触头弹簧及超程' MERGE (c_c05b)-[:FIXED_BY]->(st_c05b)
MERGE (st_c05c:Step {uid: 'ST_C05C'}) SET st_c05c.name='排除机械卡阻校正衔铁' MERGE (c_c05c)-[:FIXED_BY]->(st_c05c)
MERGE (st_c05d:Step {uid: 'ST_C05D'}) SET st_c05d.name='清理极面异物' MERGE (c_c05d)-[:FIXED_BY]->(st_c05d)
MERGE (st_c05e:Step {uid: 'ST_C05E'}) SET st_c05e.name='铜焊接好或更换短路环' MERGE (c_short_ring)-[:FIXED_BY]->(st_c05e)
MERGE (st_c06a:Step {uid: 'ST_C06A'}) SET st_c06a.name='选合适接触器/排短路/查电压/修触头/换弹簧' MERGE (c_c06a)-[:FIXED_BY]->(st_c06a)
MERGE (st_c07a:Step {uid: 'ST_C07A'}) SET st_c07a.name='调弹簧至规定值/清表面紧固/磨损>1/3换新/降容' MERGE (c_c07a)-[:FIXED_BY]->(st_c07a)
MERGE (st_c08a:Step {uid: 'ST_C08A'}) SET st_c08a.name='降容或换频繁型/调同步/排短路换触头' MERGE (c_c08a)-[:FIXED_BY]->(st_c08a)


// ==================== 三、电动机 (共享 Cause + 多步流程) ====================

// --- Symptoms ---
MERGE (s_m01:Symptom {uid: 'S_MOTOR_01'}) SET s_m01.name='电动机不能起动', s_m01.primary_features=['不能起动','无反应'], s_m01.secondary_features=['熔断器熔断','断路器跳闸'], s_m01.source_page='第五章第三节', s_m01.created_at=timestamp() MERGE (s_m01)-[:BELONGS_TO]->(e_async)
MERGE (s_m02:Symptom {uid: 'S_MOTOR_02'}) SET s_m02.name='电动机过热或冒烟', s_m02.primary_features=['过热','冒烟','焦味'], s_m02.sensory_type=['visual','olfactory','tactile'], s_m02.source_page='第五章第三节', s_m02.created_at=timestamp() MERGE (s_m02)-[:BELONGS_TO]->(e_async)
MERGE (s_m03:Symptom {uid: 'S_MOTOR_03'}) SET s_m03.name='电动机运行时噪声大', s_m03.primary_features=['噪声','异响'], s_m03.sensory_type=['auditory'], s_m03.source_page='第五章第三节', s_m03.created_at=timestamp() MERGE (s_m03)-[:BELONGS_TO]->(e_async)

// S_M01 Causes
MERGE (c_m01a:Cause {uid: 'C_MOTOR_01a'}) SET c_m01a.name='电源未接通或断相', c_m01a.check_method='measure', c_m01a.check_time='2分钟', c_m01a.failure_rate=0.35, c_m01a.created_at=timestamp() MERGE (s_m01)-[r_m01a:CAUSED_BY]->(c_m01a) SET r_m01a.priority=1
MERGE (c_m01b:Cause {uid: 'C_MOTOR_01b'}) SET c_m01b.name='定子绕组断路', c_m01b.check_method='measure', c_m01b.check_time='5分钟', c_m01b.requires_shutdown=true, c_m01b.created_at=timestamp() MERGE (s_m01)-[r_m01b:CAUSED_BY]->(c_m01b) SET r_m01b.priority=2
MERGE (c_m01c:Cause {uid: 'C_MOTOR_01c'}) SET c_m01c.name='定子绕组接地', c_m01c.check_method='measure', c_m01c.check_time='5分钟', c_m01c.requires_shutdown=true, c_m01c.requires_disassembly=true, c_m01c.failure_rate=0.08, c_m01c.created_at=timestamp() MERGE (s_m01)-[r_m01c:CAUSED_BY]->(c_m01c) SET r_m01c.priority=3
MERGE (c_m01d:Cause {uid: 'C_MOTOR_01d'}) SET c_m01d.name='绕组接线错误', c_m01d.check_method='measure', c_m01d.check_time='10分钟', c_m01d.requires_shutdown=true, c_m01d.created_at=timestamp() MERGE (s_m01)-[r_m01d:CAUSED_BY]->(c_m01d) SET r_m01d.priority=4
MERGE (c_m01e:Cause {uid: 'C_MOTOR_01e'}) SET c_m01e.name='笼型转子断笼', c_m01e.check_method='measure', c_m01e.check_time='15分钟', c_m01e.requires_shutdown=true, c_m01e.requires_disassembly=true, c_m01e.created_at=timestamp() MERGE (s_m01)-[r_m01e:CAUSED_BY]->(c_m01e) SET r_m01e.priority=5
MERGE (c_m01f:Cause {uid: 'C_MOTOR_01f'}) SET c_m01f.name='轴承损坏', c_m01f.check_method='visual', c_m01f.check_time='5分钟', c_m01f.requires_shutdown=true, c_m01f.failure_rate=0.20, c_m01f.created_at=timestamp() MERGE (s_m01)-[r_m01f:CAUSED_BY]->(c_m01f) SET r_m01f.priority=6
MERGE (c_m01g:Cause {uid: 'C_MOTOR_01g'}) SET c_m01g.name='负载机械卡死', c_m01g.check_method='visual', c_m01g.check_time='3分钟', c_m01g.created_at=timestamp() MERGE (s_m01)-[r_m01g:CAUSED_BY]->(c_m01g) SET r_m01g.priority=7
MERGE (s_m01)-[r_m01h:CAUSED_BY]->(c_voltage_low) SET r_m01h.priority=8, r_m01h.context='电压低起动转矩不足'

// S_M02 Causes
MERGE (c_m02a:Cause {uid: 'C_MOTOR_02a'}) SET c_m02a.name='长期过载运行', c_m02a.check_method='measure', c_m02a.check_time='2分钟', c_m02a.failure_rate=0.30, c_m02a.created_at=timestamp() MERGE (s_m02)-[r_m02a:CAUSED_BY]->(c_m02a) SET r_m02a.priority=1
MERGE (c_m02b:Cause {uid: 'C_MOTOR_02b'}) SET c_m02b.name='定子匝间短路/接地/断相/散热差/定转子擦', c_m02b.check_method='measure', c_m02b.check_time='10分钟', c_m02b.created_at=timestamp() MERGE (s_m02)-[r_m02b:CAUSED_BY]->(c_m02b) SET r_m02b.priority=2

// S_M03 Causes
MERGE (c_m03a:Cause {uid: 'C_MOTOR_03a'}) SET c_m03a.name='电磁噪声(电流不对称/气隙不均)', c_m03a.check_method='measure', c_m03a.check_time='3分钟', c_m03a.created_at=timestamp() MERGE (s_m03)-[r_m03a:CAUSED_BY]->(c_m03a) SET r_m03a.priority=1
MERGE (c_m03b:Cause {uid: 'C_MOTOR_03b'}) SET c_m03b.name='机械噪声(轴承磨损/风叶碰壳/不平衡)', c_m03b.check_method='visual', c_m03b.check_time='3分钟', c_m03b.failure_rate=0.25, c_m03b.created_at=timestamp() MERGE (s_m03)-[r_m03b:CAUSED_BY]->(c_m03b) SET r_m03b.priority=2

// --- 多步流程: 定子绕组接地 (3步) ---
MERGE (st_m01c_1:Step {uid: 'ST_M01C_1'}) SET st_m01c_1.name='测量对地绝缘电阻', st_m01c_1.description='500V绝缘电阻表L端接绕组E端接外壳120r/min读取', st_m01c_1.duration='5分钟', st_m01c_1.min_personnel=1, st_m01c_1.safety_level='normal', st_m01c_1.source_page='第五章第三节', st_m01c_1.created_at=timestamp()
MERGE (st_m01c_2:Step {uid: 'ST_M01C_2'}) SET st_m01c_2.name='查找接地点', st_m01c_2.description='解体目视绕组端部槽口绝缘；校验灯串联220V通电找火花；或升压法500~1000V使接地点击穿跳火', st_m01c_2.duration='30分钟', st_m01c_2.min_personnel=2, st_m01c_2.safety_level='danger', st_m01c_2.source_page='第五章第三节', st_m01c_2.created_at=timestamp()
MERGE (st_m01c_3:Step {uid: 'ST_M01C_3'}) SET st_m01c_3.name='修复接地故障', st_m01c_3.description='加热绕组至80~100°C软化撬开导线垫0.15~0.25mm青壳纸；损伤超1/12拆除线圈重绕', st_m01c_3.duration='2小时', st_m01c_3.min_personnel=2, st_m01c_3.safety_level='caution', st_m01c_3.source_page='第五章第三节', st_m01c_3.created_at=timestamp()
MERGE (c_m01c)-[:FIXED_BY]->(st_m01c_1)
MERGE (st_m01c_1)-[:NEXT_STEP]->(st_m01c_2)
MERGE (st_m01c_2)-[:NEXT_STEP]->(st_m01c_3)

// --- 多步流程: 电动机噪声诊断 (2步) ---
MERGE (st_m03a_1:Step {uid: 'ST_M03A_1'}) SET st_m03a_1.name='空载切电源判断噪声来源', st_m03a_1.duration='3分钟', st_m03a_1.min_personnel=1, st_m03a_1.safety_level='normal', st_m03a_1.created_at=timestamp()
MERGE (st_m03a_2:Step {uid: 'ST_M03A_2'}) SET st_m03a_2.name='电磁噪声查绕组电源/机械噪声查轴承风叶动平衡', st_m03a_2.duration='15分钟', st_m03a_2.min_personnel=1, st_m03a_2.created_at=timestamp()
MERGE (c_m03a)-[:FIXED_BY]->(st_m03a_1)
MERGE (st_m03a_1)-[:NEXT_STEP]->(st_m03a_2)

// --- 单步修复 ---
MERGE (st_m01a:Step {uid: 'ST_M01A'}) SET st_m01a.name='万用表500V档测接线盒三相电压逐级查断路器熔断器' MERGE (c_m01a)-[:FIXED_BY]->(st_m01a)
MERGE (st_m01f:Step {uid: 'ST_M01F'}) SET st_m01f.name='更换同型号轴承热套法油温≤120°C' MERGE (c_m01f)-[:FIXED_BY]->(st_m01f)
MERGE (st_m01g:Step {uid: 'ST_M01G'}) SET st_m01g.name='检查排除机械卡阻' MERGE (c_m01g)-[:FIXED_BY]->(st_m01g)
MERGE (st_m01h:Step {uid: 'ST_M01H'}) SET st_m01h.name='调整电源电压至额定值' MERGE (c_voltage_low)-[:FIXED_BY]->(st_m01h)
MERGE (st_m02a:Step {uid: 'ST_M02A'}) SET st_m02a.name='减小负载至额定值以下' MERGE (c_m02a)-[:FIXED_BY]->(st_m02a)
MERGE (st_m02b:Step {uid: 'ST_M02B'}) SET st_m02b.name='查短路查熔断器触头清风扇换轴承调气隙' MERGE (c_m02b)-[:FIXED_BY]->(st_m02b)


// ==================== 四、备件/工具/注意事项 ====================

MERGE (sp_coil:SparePart {uid: 'SP_COIL'}) SET sp_coil.name='接触器/继电器线圈'
MERGE (sp_contact:SparePart {uid: 'SP_CONTACT'}) SET sp_contact.name='触头组件'
MERGE (sp_arc:SparePart {uid: 'SP_ARC_CHUTE'}) SET sp_arc.name='灭弧罩'
MERGE (sp_ring:SparePart {uid: 'SP_SHORT_RING'}) SET sp_ring.name='短路环'
MERGE (sp_spring:SparePart {uid: 'SP_SPRING'}) SET sp_spring.name='弹簧'
MERGE (sp_bearing:SparePart {uid: 'SP_BEARING'}) SET sp_bearing.name='滚动轴承'
MERGE (sp_brush:SparePart {uid: 'SP_BRUSH'}) SET sp_brush.name='电刷'
MERGE (sp_fuse:SparePart {uid: 'SP_FUSE'}) SET sp_fuse.name='熔断器熔体'
MERGE (sp_insul:SparePart {uid: 'SP_INSUL'}) SET sp_insul.name='绝缘材料', sp_insul.description='聚酯薄膜0.055mm或青壳纸0.15mm'
MERGE (sp_fric:SparePart {uid: 'SP_FRICTION'}) SET sp_fric.name='摩擦片/块'
MERGE (sp_therm:SparePart {uid: 'SP_THERMAL'}) SET sp_therm.name='热继电器'
MERGE (sp_plc:SparePart {uid: 'SP_PLC_IO'}) SET sp_plc.name='PLC接口模块'
MERGE (sp_pcb:SparePart {uid: 'SP_PCB'}) SET sp_pcb.name='印制电路板'
MERGE (sp_sensor:SparePart {uid: 'SP_SENSOR'}) SET sp_sensor.name='传感器'
MERGE (sp_seal:SparePart {uid: 'SP_SEAL'}) SET sp_seal.name='密封圈/垫圈'

MERGE (t_mm:Tool {uid: 'T_MULTIMETER'}) SET t_mm.name='万用表', t_mm.functions=['measure_voltage','measure_current','measure_resistance'], t_mm.alternatives=['T_BRIDGE']
MERGE (t_megger:Tool {uid: 'T_MEGGER'}) SET t_megger.name='绝缘电阻表', t_megger.functions=['measure_insulation'], t_megger.alternatives=[]
MERGE (t_clamp:Tool {uid: 'T_CLAMP'}) SET t_clamp.name='钳形电流表', t_clamp.functions=['measure_current_noncontact']
MERGE (t_short:Tool {uid: 'T_SHORT_TESTER'}) SET t_short.name='短路侦察器', t_short.functions=['detect_short_circuit','detect_broken_bar']
MERGE (t_bridge:Tool {uid: 'T_BRIDGE'}) SET t_bridge.name='电桥', t_bridge.functions=['measure_resistance_precise'], t_bridge.alternatives=['T_MULTIMETER']
MERGE (t_solder:Tool {uid: 'T_SOLDRON'}) SET t_solder.name='电烙铁', t_solder.functions=['solder']
MERGE (t_puller:Tool {uid: 'T_PULLER'}) SET t_puller.name='轴承拉拔器', t_puller.functions=['remove_bearing']

MERGE (p_disc:Precaution {uid: 'P_DISCONNECT'}) SET p_disc.name='断电挂牌', p_disc.severity='forbidden', p_disc.consequence='触电致死', p_disc.consequence_type='injury', p_disc.description='切断电源挂禁止合闸告示牌'
MERGE (p_cap:Precaution {uid: 'P_CAP_DISCHARGE'}) SET p_cap.name='电容放电', p_cap.severity='forbidden', p_cap.consequence='电击伤人', p_cap.consequence_type='injury', p_cap.description='电容充分放电2~3min后测量'
MERGE (p_no_live:Precaution {uid: 'P_NO_LIVE_RES'}) SET p_no_live.name='禁带电测电阻', p_no_live.severity='forbidden', p_no_live.consequence='烧万用表', p_no_live.consequence_type='equipment_damage'
MERGE (p_megger_ban:Precaution {uid: 'P_MEGGER_BAN'}) SET p_megger_ban.name='禁测电子设备', p_megger_ban.severity='forbidden', p_megger_ban.consequence='击穿元件', p_megger_ban.consequence_type='equipment_damage'
MERGE (p_hv:Precaution {uid: 'P_HIGH_V_GUARD'}) SET p_hv.name='高压试验监护', p_hv.severity='forbidden', p_hv.consequence='电击致死', p_hv.consequence_type='injury', p_hv.description='升压法须专人监护远离高压部位'
MERGE (p_dry:Precaution {uid: 'P_DRY_TEMP'}) SET p_dry.name='绕组烘干控温', p_dry.severity='warning', p_dry.consequence='绝缘开裂', p_dry.consequence_type='equipment_damage', p_dry.description='E级≤120°C B级≤130°C'
MERGE (p_sync:Precaution {uid: 'P_SYNC_CONTACT'}) SET p_sync.name='三相触头同步', p_sync.severity='warning', p_sync.consequence='断相烧电机', p_sync.consequence_type='equipment_damage'

// ==================== Step 关联备件/工具/安全 ====================
// 电动机绕组接地三步关联
MATCH (st:Step {uid: 'ST_M01C_1'}) MATCH (t:Tool {uid: 'T_MEGGER'}) MERGE (st)-[:REQUIRES_TOOL]->(t)
MATCH (st:Step {uid: 'ST_M01C_1'}) MATCH (p:Precaution {uid: 'P_DISCONNECT'}) MERGE (st)-[:HAS_PRECAUTION]->(p)
MATCH (st:Step {uid: 'ST_M01C_1'}) MATCH (p:Precaution {uid: 'P_CAP_DISCHARGE'}) MERGE (st)-[:HAS_PRECAUTION]->(p)
MATCH (st:Step {uid: 'ST_M01C_2'}) MATCH (t:Tool {uid: 'T_MULTIMETER'}) MERGE (st)-[:REQUIRES_TOOL]->(t)
MATCH (st:Step {uid: 'ST_M01C_2'}) MATCH (t:Tool {uid: 'T_MEGGER'}) MERGE (st)-[:REQUIRES_TOOL]->(t)
MATCH (st:Step {uid: 'ST_M01C_2'}) MATCH (p:Precaution {uid: 'P_DISCONNECT'}) MERGE (st)-[:HAS_PRECAUTION]->(p)
MATCH (st:Step {uid: 'ST_M01C_2'}) MATCH (p:Precaution {uid: 'P_HIGH_V_GUARD'}) MERGE (st)-[:HAS_PRECAUTION]->(p)
MATCH (st:Step {uid: 'ST_M01C_3'}) MATCH (sp:SparePart {uid: 'SP_INSUL'}) MERGE (st)-[:USES_SPAREPART]->(sp)
MATCH (st:Step {uid: 'ST_M01C_3'}) MATCH (p:Precaution {uid: 'P_DRY_TEMP'}) MERGE (st)-[:HAS_PRECAUTION]->(p)

// 短路环更换关联
MATCH (st:Step {uid: 'ST_C05E'}) MATCH (sp:SparePart {uid: 'SP_SHORT_RING'}) MERGE (st)-[:USES_SPAREPART]->(sp)
MATCH (st:Step {uid: 'ST_C05E'}) MATCH (t:Tool {uid: 'T_SOLDRON'}) MERGE (st)-[:REQUIRES_TOOL]->(t)
MATCH (st:Step {uid: 'ST_C05E'}) MATCH (p:Precaution {uid: 'P_DISCONNECT'}) MERGE (st)-[:HAS_PRECAUTION]->(p)
MATCH (st:Step {uid: 'ST_C01D'}) MATCH (p:Precaution {uid: 'P_DISCONNECT'}) MERGE (st)-[:HAS_PRECAUTION]->(p)
MATCH (st:Step {uid: 'ST_C01A'}) MATCH (t:Tool {uid: 'T_MULTIMETER'}) MERGE (st)-[:REQUIRES_TOOL]->(t)

// ==================== 导入完成 ====================
MATCH (eq:Equipment) WITH count(eq) AS 设备数
MATCH (s:Symptom) WITH 设备数, count(s) AS 现象数
MATCH (c:Cause) WITH 设备数, 现象数, count(c) AS 原因数
MATCH (st:Step) WITH 设备数, 现象数, 原因数, count(st) AS 步骤数
MATCH (sp:SparePart) WITH 设备数, 现象数, 原因数, 步骤数, count(sp) AS 备件数
MATCH (t:Tool) WITH 设备数, 现象数, 原因数, 步骤数, 备件数, count(t) AS 工具数
MATCH (p:Precaution) WITH 设备数, 现象数, 原因数, 步骤数, 备件数, 工具数, count(p) AS 安全数
MATCH ()-[r]->() WITH 设备数, 现象数, 原因数, 步骤数, 备件数, 工具数, 安全数, count(r) AS 关系总数
RETURN 'v4.0 导入完成' AS 状态, 设备数, 现象数, 原因数, 步骤数, 备件数, 工具数, 安全数, 关系总数
