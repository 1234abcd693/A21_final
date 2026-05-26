// ============================================================================
// A21 知识图谱批量扩充 — 覆盖全部设备类型的常见故障
// 扩充目标: +350 实体 +200 关系 → 总计 500+ 实体 350+ 关系
// ============================================================================

// ==================== 接触器 (续) ====================

// --- 新增 Cause ---
MERGE (c_ex_01:Cause {uid: 'C_EX_001'}) SET c_ex_01.name='控制回路接线松动', c_ex_01.check_method='visual', c_ex_01.check_time='2分钟', c_ex_01.created_at=timestamp()
MERGE (c_ex_02:Cause {uid: 'C_EX_002'}) SET c_ex_02.name='线圈引线脱焊或断路', c_ex_02.check_method='visual', c_ex_02.check_time='2分钟', c_ex_02.created_at=timestamp()
MERGE (c_ex_03:Cause {uid: 'C_EX_003'}) SET c_ex_03.name='触头弹簧压力不足', c_ex_03.check_method='measure', c_ex_03.check_time='3分钟', c_ex_03.requires_shutdown=true, c_ex_03.created_at=timestamp()
MERGE (c_ex_04:Cause {uid: 'C_EX_004'}) SET c_ex_04.name='触头超程过小', c_ex_04.check_method='measure', c_ex_04.check_time='2分钟', c_ex_04.created_at=timestamp()
MERGE (c_ex_05:Cause {uid: 'C_EX_005'}) SET c_ex_05.name='灭弧罩破损或碳化', c_ex_05.check_method='visual', c_ex_05.check_time='1分钟', c_ex_05.created_at=timestamp()
MERGE (c_ex_06:Cause {uid: 'C_EX_006'}) SET c_ex_06.name='衔铁反力弹簧失效或缺损', c_ex_06.check_method='visual', c_ex_06.check_time='2分钟', c_ex_06.created_at=timestamp()
MERGE (c_ex_07:Cause {uid: 'C_EX_007'}) SET c_ex_07.name='铁心极面有油泥黏着', c_ex_07.check_method='visual', c_ex_07.check_time='1分钟', c_ex_07.created_at=timestamp()

// --- 新增 Step ---
MERGE (st_ex_01:Step {uid: 'ST_EX_001'}) SET st_ex_01.name='检查并紧固所有接线端子', st_ex_01.created_at=timestamp()
MERGE (st_ex_02:Step {uid: 'ST_EX_002'}) SET st_ex_02.name='拆下线圈检查引线焊点', st_ex_02.created_at=timestamp()
MERGE (st_ex_03:Step {uid: 'ST_EX_003'}) SET st_ex_03.name='调整触头弹簧压力至规定值', st_ex_03.created_at=timestamp()
MERGE (st_ex_04:Step {uid: 'ST_EX_004'}) SET st_ex_04.name='调整触头超程至规定值', st_ex_04.created_at=timestamp()
MERGE (st_ex_05:Step {uid: 'ST_EX_005'}) SET st_ex_05.name='更换灭弧罩', st_ex_05.created_at=timestamp()
MERGE (st_ex_06:Step {uid: 'ST_EX_006'}) SET st_ex_06.name='清理铁心极面油污', st_ex_06.created_at=timestamp()
MERGE (st_ex_07:Step {uid: 'ST_EX_007'}) SET st_ex_07.name='更换衔铁反力弹簧', st_ex_07.created_at=timestamp()
MERGE (st_ex_08:Step {uid: 'ST_EX_008'}) SET st_ex_08.name='检查线圈温升，若≥65℃查明原因', st_ex_08.created_at=timestamp()
MERGE (st_ex_09:Step {uid: 'ST_EX_009'}) SET st_ex_09.name='用砂纸打磨焊头处漆皮，涂中性焊剂焊牢', st_ex_09.created_at=timestamp()
MERGE (st_ex_10:Step {uid: 'ST_EX_010'}) SET st_ex_10.name='用黄蜡绸带包好做绝缘处理', st_ex_10.created_at=timestamp()
MERGE (st_ex_11:Step {uid: 'ST_EX_011'}) SET st_ex_11.name='重新绕制线圈', st_ex_11.created_at=timestamp()
MERGE (st_ex_12:Step {uid: 'ST_EX_012'}) SET st_ex_12.name='断电后用万用表电阻档测量线圈电阻', st_ex_12.created_at=timestamp()

// ==================== 电动机 ====================

// --- 电动机 Causes ---
MERGE (c_m_01:Cause {uid: 'C_MOTOR_001'}) SET c_m_01.name='三相电源缺相', c_m_01.check_method='measure', c_m_01.check_time='2分钟', c_m_01.created_at=timestamp()
MERGE (c_m_02:Cause {uid: 'C_MOTOR_002'}) SET c_m_02.name='定子绕组断路', c_m_02.check_method='measure', c_m_02.check_time='5分钟', c_m_02.requires_shutdown=true, c_m_02.created_at=timestamp()
MERGE (c_m_03:Cause {uid: 'C_MOTOR_003'}) SET c_m_03.name='定子绕组接地', c_m_03.check_method='measure', c_m_03.check_time='5分钟', c_m_03.requires_shutdown=true, c_m_03.created_at=timestamp()
MERGE (c_m_04:Cause {uid: 'C_MOTOR_004'}) SET c_m_04.name='定子绕组匝间短路', c_m_04.check_method='measure', c_m_04.check_time='5分钟', c_m_04.requires_shutdown=true, c_m_04.created_at=timestamp()
MERGE (c_m_05:Cause {uid: 'C_MOTOR_005'}) SET c_m_05.name='转子断条或铸铝缺陷', c_m_05.check_method='measure', c_m_05.check_time='10分钟', c_m_05.requires_shutdown=true, c_m_05.created_at=timestamp()
MERGE (c_m_06:Cause {uid: 'C_MOTOR_006'}) SET c_m_06.name='轴承损坏', c_m_06.check_method='visual', c_m_06.check_time='3分钟', c_m_06.requires_shutdown=true, c_m_06.created_at=timestamp()
MERGE (c_m_07:Cause {uid: 'C_MOTOR_007'}) SET c_m_07.name='轴承缺油或油脂老化', c_m_07.check_method='visual', c_m_07.check_time='2分钟', c_m_07.created_at=timestamp()
MERGE (c_m_08:Cause {uid: 'C_MOTOR_008'}) SET c_m_08.name='转子不平衡', c_m_08.check_method='measure', c_m_08.check_time='5分钟', c_m_08.created_at=timestamp()
MERGE (c_m_09:Cause {uid: 'C_MOTOR_009'}) SET c_m_09.name='地脚螺栓松动', c_m_09.check_method='visual', c_m_09.check_time='1分钟', c_m_09.created_at=timestamp()
MERGE (c_m_10:Cause {uid: 'C_MOTOR_010'}) SET c_m_10.name='联轴器不对中', c_m_10.check_method='measure', c_m_10.check_time='5分钟', c_m_10.created_at=timestamp()
MERGE (c_m_11:Cause {uid: 'C_MOTOR_011'}) SET c_m_11.name='通风道堵塞', c_m_11.check_method='visual', c_m_11.check_time='1分钟', c_m_11.created_at=timestamp()
MERGE (c_m_12:Cause {uid: 'C_MOTOR_012'}) SET c_m_12.name='风扇损坏或风罩缺失', c_m_12.check_method='visual', c_m_12.check_time='2分钟', c_m_12.created_at=timestamp()
MERGE (c_m_13:Cause {uid: 'C_MOTOR_013'}) SET c_m_13.name='负载过大或堵转', c_m_13.check_method='measure', c_m_13.check_time='3分钟', c_m_13.created_at=timestamp()
MERGE (c_m_14:Cause {uid: 'C_MOTOR_014'}) SET c_m_14.name='绕组受潮绝缘降低', c_m_14.check_method='measure', c_m_14.check_time='3分钟', c_m_14.created_at=timestamp()
MERGE (c_m_15:Cause {uid: 'C_MOTOR_015'}) SET c_m_15.name='接线端子松动或氧化', c_m_15.check_method='visual', c_m_15.check_time='1分钟', c_m_15.created_at=timestamp()
MERGE (c_m_16:Cause {uid: 'C_MOTOR_016'}) SET c_m_16.name='电刷磨损或接触不良(直流电机)', c_m_16.check_method='visual', c_m_16.check_time='2分钟', c_m_16.created_at=timestamp()
MERGE (c_m_17:Cause {uid: 'C_MOTOR_017'}) SET c_m_17.name='换向器表面不平或有油污', c_m_17.check_method='visual', c_m_17.check_time='2分钟', c_m_17.created_at=timestamp()
MERGE (c_m_18:Cause {uid: 'C_MOTOR_018'}) SET c_m_18.name='励磁绕组断路', c_m_18.check_method='measure', c_m_18.check_time='5分钟', c_m_18.created_at=timestamp()
MERGE (c_m_19:Cause {uid: 'C_MOTOR_019'}) SET c_m_19.name='控制回路接线错误', c_m_19.check_method='visual', c_m_19.check_time='2分钟', c_m_19.created_at=timestamp()
MERGE (c_m_20:Cause {uid: 'C_MOTOR_020'}) SET c_m_20.name='熔断器熔断', c_m_20.check_method='visual', c_m_20.check_time='1分钟', c_m_20.created_at=timestamp()

// --- 电动机 Steps ---
MERGE (st_m_01:Step {uid: 'ST_MOTOR_001'}) SET st_m_01.name='用万用表500V档测量三相电源电压', st_m_01.created_at=timestamp()
MERGE (st_m_02:Step {uid: 'ST_MOTOR_002'}) SET st_m_02.name='用绝缘电阻表测量定子绕组对地绝缘', st_m_02.created_at=timestamp()
MERGE (st_m_03:Step {uid: 'ST_MOTOR_003'}) SET st_m_03.name='测量三相绕组直流电阻判断是否平衡', st_m_03.created_at=timestamp()
MERGE (st_m_04:Step {uid: 'ST_MOTOR_004'}) SET st_m_04.name='检查并紧固所有接线端子', st_m_04.created_at=timestamp()
MERGE (st_m_05:Step {uid: 'ST_MOTOR_005'}) SET st_m_05.name='用短路侦察器检查转子断条', st_m_05.created_at=timestamp()
MERGE (st_m_06:Step {uid: 'ST_MOTOR_006'}) SET st_m_06.name='拆卸轴承检查磨损情况', st_m_06.created_at=timestamp()
MERGE (st_m_07:Step {uid: 'ST_MOTOR_007'}) SET st_m_07.name='更换轴承并添加新润滑脂', st_m_07.created_at=timestamp()
MERGE (st_m_08:Step {uid: 'ST_MOTOR_008'}) SET st_m_08.name='对绕组进行干燥处理(堵转电流法)', st_m_08.created_at=timestamp()
MERGE (st_m_09:Step {uid: 'ST_MOTOR_009'}) SET st_m_09.name='清理通风道和风扇罩', st_m_09.created_at=timestamp()
MERGE (st_m_10:Step {uid: 'ST_MOTOR_010'}) SET st_m_10.name='紧固地脚螺栓至规定力矩', st_m_10.created_at=timestamp()
MERGE (st_m_11:Step {uid: 'ST_MOTOR_011'}) SET st_m_11.name='校正联轴器对中', st_m_11.created_at=timestamp()
MERGE (st_m_12:Step {uid: 'ST_MOTOR_012'}) SET st_m_12.name='更换电刷并研磨换向器表面', st_m_12.created_at=timestamp()
MERGE (st_m_13:Step {uid: 'ST_MOTOR_013'}) SET st_m_13.name='绕组重绕或更换电机', st_m_13.created_at=timestamp()
MERGE (st_m_14:Step {uid: 'ST_MOTOR_014'}) SET st_m_14.name='检查并更换熔断器', st_m_14.created_at=timestamp()
MERGE (st_m_15:Step {uid: 'ST_MOTOR_015'}) SET st_m_15.name='测量空载电流与额定值对比', st_m_15.created_at=timestamp()

// --- 电动机 Symptoms ---
MERGE (s_m_new01:Symptom {uid: 'S_MOTOR_N01'}) SET s_m_new01.name='电动机不能起动', s_m_new01.primary_features=['不能起动','无法启动','不能启动'], s_m_new01.source_doc='船舶电气设备维护与修理', s_m_new01.source_page='第五章第三节', s_m_new01.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_ASYNCH_MOTOR'}) MERGE (s_m_new01)-[:BELONGS_TO]->(e)
MERGE (s_m_new01)-[:CAUSED_BY {priority:1}]->(c_m_01) MERGE (s_m_new01)-[:CAUSED_BY {priority:2}]->(c_voltage_low)
MERGE (s_m_new01)-[:CAUSED_BY {priority:3}]->(c_m_02) MERGE (s_m_new01)-[:CAUSED_BY {priority:4}]->(c_m_03)
MERGE (s_m_new01)-[:CAUSED_BY {priority:5}]->(c_m_19) MERGE (s_m_new01)-[:CAUSED_BY {priority:6}]->(c_m_20)
MERGE (c_m_01)-[:FIXED_BY]->(st_m_01) MERGE (st_m_01)-[:NEXT_STEP]->(st_m_14) MERGE (st_m_14)-[:NEXT_STEP]->(st_m_04)
MERGE (c_voltage_low)-[:FIXED_BY]->(st_m_01) MERGE (c_m_02)-[:FIXED_BY]->(st_m_03) MERGE (c_m_03)-[:FIXED_BY]->(st_m_02)

MERGE (s_m_new02:Symptom {uid: 'S_MOTOR_N02'}) SET s_m_new02.name='电动机过热或冒烟', s_m_new02.primary_features=['过热','冒烟','发热','温度高'], s_m_new02.source_doc='船舶电气设备维护与修理', s_m_new02.source_page='第五章第三节', s_m_new02.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_ASYNCH_MOTOR'}) MERGE (s_m_new02)-[:BELONGS_TO]->(e)
MERGE (s_m_new02)-[:CAUSED_BY {priority:1}]->(c_m_13) MERGE (s_m_new02)-[:CAUSED_BY {priority:2}]->(c_m_04)
MERGE (s_m_new02)-[:CAUSED_BY {priority:3}]->(c_m_11) MERGE (s_m_new02)-[:CAUSED_BY {priority:4}]->(c_m_12)
MERGE (s_m_new02)-[:CAUSED_BY {priority:5}]->(c_m_14) MERGE (s_m_new02)-[:CAUSED_BY {priority:6}]->(c_m_01)
MERGE (c_m_13)-[:FIXED_BY]->(st_m_15) MERGE (c_m_04)-[:FIXED_BY]->(st_m_03) MERGE (c_m_11)-[:FIXED_BY]->(st_m_09)

MERGE (s_m_new03:Symptom {uid: 'S_MOTOR_N03'}) SET s_m_new03.name='电动机振动异常或异响', s_m_new03.primary_features=['振动','异响','噪音','震动'], s_m_new03.source_doc='船舶电气设备维护与修理', s_m_new03.source_page='第五章第三节', s_m_new03.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_ASYNCH_MOTOR'}) MERGE (s_m_new03)-[:BELONGS_TO]->(e)
MERGE (s_m_new03)-[:CAUSED_BY {priority:1}]->(c_m_06) MERGE (s_m_new03)-[:CAUSED_BY {priority:2}]->(c_m_08)
MERGE (s_m_new03)-[:CAUSED_BY {priority:3}]->(c_m_09) MERGE (s_m_new03)-[:CAUSED_BY {priority:4}]->(c_m_10)
MERGE (s_m_new03)-[:CAUSED_BY {priority:5}]->(c_m_01)
MERGE (c_m_06)-[:FIXED_BY]->(st_m_06) MERGE (st_m_06)-[:NEXT_STEP]->(st_m_07) MERGE (c_m_09)-[:FIXED_BY]->(st_m_10)

MERGE (s_m_new04:Symptom {uid: 'S_MOTOR_N04'}) SET s_m_new04.name='电动机转速低或转速不稳', s_m_new04.primary_features=['转速低','转速不稳','转速波动','无力'], s_m_new04.source_doc='船舶电气设备维护与修理', s_m_new04.source_page='第五章第三节', s_m_new04.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_ASYNCH_MOTOR'}) MERGE (s_m_new04)-[:BELONGS_TO]->(e)
MERGE (s_m_new04)-[:CAUSED_BY {priority:1}]->(c_m_13) MERGE (s_m_new04)-[:CAUSED_BY {priority:2}]->(c_m_01)
MERGE (s_m_new04)-[:CAUSED_BY {priority:3}]->(c_m_05) MERGE (s_m_new04)-[:CAUSED_BY {priority:4}]->(c_voltage_low)

MERGE (s_m_new05:Symptom {uid: 'S_MOTOR_N05'}) SET s_m_new05.name='电动机绝缘电阻过低', s_m_new05.primary_features=['绝缘低','漏电','绝缘电阻低'], s_m_new05.source_doc='船舶电气设备维护与修理', s_m_new05.source_page='第五章第三节', s_m_new05.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_ASYNCH_MOTOR'}) MERGE (s_m_new05)-[:BELONGS_TO]->(e)
MERGE (s_m_new05)-[:CAUSED_BY {priority:1}]->(c_m_14) MERGE (s_m_new05)-[:CAUSED_BY {priority:2}]->(c_m_03)
MERGE (c_m_14)-[:FIXED_BY]->(st_m_08) MERGE (c_m_03)-[:FIXED_BY]->(st_m_02)

// --- 直流电机 Symptoms ---
MERGE (s_dc01:Symptom {uid: 'S_DC_N01'}) SET s_dc01.name='直流电机不能起动', s_dc01.source_doc='船舶电气设备维护与修理', s_dc01.source_page='第五章第四节', s_dc01.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_DC_MOTOR'}) MERGE (s_dc01)-[:BELONGS_TO]->(e)
MERGE (s_dc01)-[:CAUSED_BY {priority:1}]->(c_m_01) MERGE (s_dc01)-[:CAUSED_BY {priority:2}]->(c_m_16)
MERGE (s_dc01)-[:CAUSED_BY {priority:3}]->(c_m_18)

MERGE (s_dc02:Symptom {uid: 'S_DC_N02'}) SET s_dc02.name='直流电机火花过大', s_dc02.source_doc='船舶电气设备维护与修理', s_dc02.source_page='第五章第四节', s_dc02.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_DC_MOTOR'}) MERGE (s_dc02)-[:BELONGS_TO]->(e)
MERGE (s_dc02)-[:CAUSED_BY {priority:1}]->(c_m_16) MERGE (s_dc02)-[:CAUSED_BY {priority:2}]->(c_m_17)
MERGE (c_m_16)-[:FIXED_BY]->(st_m_12)

// ==================== 发电机 ====================

MERGE (c_g_01:Cause {uid: 'C_GEN_001'}) SET c_g_01.name='剩磁消失', c_g_01.check_method='measure', c_g_01.check_time='3分钟', c_g_01.created_at=timestamp()
MERGE (c_g_02:Cause {uid: 'C_GEN_002'}) SET c_g_02.name='励磁线圈接反', c_g_02.check_method='visual', c_g_02.check_time='2分钟', c_g_02.created_at=timestamp()
MERGE (c_g_03:Cause {uid: 'C_GEN_003'}) SET c_g_03.name='励磁绕组断路', c_g_03.check_method='measure', c_g_03.check_time='5分钟', c_g_03.created_at=timestamp()
MERGE (c_g_04:Cause {uid: 'C_GEN_004'}) SET c_g_04.name='电枢线圈匝间短路', c_g_04.check_method='measure', c_g_04.check_time='5分钟', c_g_04.created_at=timestamp()
MERGE (c_g_05:Cause {uid: 'C_GEN_005'}) SET c_g_05.name='换向片间短路', c_g_05.check_method='measure', c_g_05.check_time='5分钟', c_g_05.created_at=timestamp()
MERGE (c_g_06:Cause {uid: 'C_GEN_006'}) SET c_g_06.name='电刷不在中性位置', c_g_06.check_method='measure', c_g_06.check_time='5分钟', c_g_06.created_at=timestamp()
MERGE (c_g_07:Cause {uid: 'C_GEN_007'}) SET c_g_07.name='AVR(自动电压调节器)故障', c_g_07.check_method='measure', c_g_07.check_time='10分钟', c_g_07.created_at=timestamp()
MERGE (c_g_08:Cause {uid: 'C_GEN_008'}) SET c_g_08.name='原动机转速过低', c_g_08.check_method='measure', c_g_08.check_time='2分钟', c_g_08.created_at=timestamp()

MERGE (st_g_01:Step {uid: 'ST_GEN_001'}) SET st_g_01.name='用直流电源给励磁绕组充磁', st_g_01.created_at=timestamp()
MERGE (st_g_02:Step {uid: 'ST_GEN_002'}) SET st_g_02.name='检查并纠正励磁线圈极性', st_g_02.created_at=timestamp()
MERGE (st_g_03:Step {uid: 'ST_GEN_003'}) SET st_g_03.name='用万用表检查励磁回路通断', st_g_03.created_at=timestamp()
MERGE (st_g_04:Step {uid: 'ST_GEN_004'}) SET st_g_04.name='调整电刷至中性位置', st_g_04.created_at=timestamp()
MERGE (st_g_05:Step {uid: 'ST_GEN_005'}) SET st_g_05.name='检查AVR接线并测试', st_g_05.created_at=timestamp()
MERGE (st_g_06:Step {uid: 'ST_GEN_006'}) SET st_g_06.name='测量电枢绕组片间电压判断短路', st_g_06.created_at=timestamp()

MERGE (s_g01:Symptom {uid: 'S_GEN_N01'}) SET s_g01.name='自励发电机不能建压', s_g01.source_doc='船舶电气设备维护与修理', s_g01.source_page='第五章第五节', s_g01.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_GENERATOR'}) MERGE (s_g01)-[:BELONGS_TO]->(e)
MERGE (s_g01)-[:CAUSED_BY {priority:1}]->(c_g_01) MERGE (s_g01)-[:CAUSED_BY {priority:2}]->(c_g_02)
MERGE (s_g01)-[:CAUSED_BY {priority:3}]->(c_g_03)
MERGE (c_g_01)-[:FIXED_BY]->(st_g_01) MERGE (c_g_02)-[:FIXED_BY]->(st_g_02)

MERGE (s_g02:Symptom {uid: 'S_GEN_N02'}) SET s_g02.name='发电机电压低', s_g02.source_doc='船舶电气设备维护与修理', s_g02.source_page='第五章第五节', s_g02.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_GENERATOR'}) MERGE (s_g02)-[:BELONGS_TO]->(e)
MERGE (s_g02)-[:CAUSED_BY {priority:1}]->(c_g_04) MERGE (s_g02)-[:CAUSED_BY {priority:2}]->(c_g_06)
MERGE (s_g02)-[:CAUSED_BY {priority:3}]->(c_g_08)

MERGE (s_g03:Symptom {uid: 'S_GEN_N03'}) SET s_g03.name='发电机电压不稳', s_g03.source_doc='船舶电气设备维护与修理', s_g03.source_page='第五章第五节', s_g03.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_GENERATOR'}) MERGE (s_g03)-[:BELONGS_TO]->(e)
MERGE (s_g03)-[:CAUSED_BY {priority:1}]->(c_g_07) MERGE (s_g03)-[:CAUSED_BY {priority:2}]->(c_g_08)

MERGE (s_g04:Symptom {uid: 'S_GEN_N04'}) SET s_g04.name='发电机过热', s_g04.source_doc='船舶电气设备维护与修理', s_g04.source_page='第五章第五节', s_g04.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_GENERATOR'}) MERGE (s_g04)-[:BELONGS_TO]->(e)
MERGE (s_g04)-[:CAUSED_BY {priority:1}]->(c_m_13) MERGE (s_g04)-[:CAUSED_BY {priority:2}]->(c_m_11)

// ==================== 变压器 ====================

MERGE (c_t_01:Cause {uid: 'C_TRANS_001'}) SET c_t_01.name='绕组匝间短路', c_t_01.check_method='measure', c_t_01.check_time='5分钟', c_t_01.created_at=timestamp()
MERGE (c_t_02:Cause {uid: 'C_TRANS_002'}) SET c_t_02.name='铁心硅钢片绝缘损坏', c_t_02.check_method='measure', c_t_02.check_time='5分钟', c_t_02.created_at=timestamp()
MERGE (c_t_03:Cause {uid: 'C_TRANS_003'}) SET c_t_03.name='紧固螺栓松动', c_t_03.check_method='visual', c_t_03.check_time='1分钟', c_t_03.created_at=timestamp()
MERGE (c_t_04:Cause {uid: 'C_TRANS_004'}) SET c_t_04.name='分接开关接触不良', c_t_04.check_method='measure', c_t_04.check_time='3分钟', c_t_04.created_at=timestamp()

MERGE (s_t01:Symptom {uid: 'S_TRANS_N01'}) SET s_t01.name='变压器过热', s_t01.source_doc='船舶电气设备维护与修理', s_t01.source_page='第五章第六节', s_t01.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_TRANSFORMER'}) MERGE (s_t01)-[:BELONGS_TO]->(e)
MERGE (s_t01)-[:CAUSED_BY {priority:1}]->(c_m_13) MERGE (s_t01)-[:CAUSED_BY {priority:2}]->(c_t_01)
MERGE (s_t01)-[:CAUSED_BY {priority:3}]->(c_t_02) MERGE (s_t01)-[:CAUSED_BY {priority:4}]->(c_m_11)

MERGE (s_t02:Symptom {uid: 'S_TRANS_N02'}) SET s_t02.name='变压器噪声大', s_t02.source_doc='船舶电气设备维护与修理', s_t02.source_page='第五章第六节', s_t02.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_TRANSFORMER'}) MERGE (s_t02)-[:BELONGS_TO]->(e)
MERGE (s_t02)-[:CAUSED_BY {priority:1}]->(c_t_03) MERGE (s_t02)-[:CAUSED_BY {priority:2}]->(c_m_13)

MERGE (s_t03:Symptom {uid: 'S_TRANS_N03'}) SET s_t03.name='变压器绝缘电阻低', s_t03.source_doc='船舶电气设备维护与修理', s_t03.source_page='第五章第六节', s_t03.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_TRANSFORMER'}) MERGE (s_t03)-[:BELONGS_TO]->(e)
MERGE (s_t03)-[:CAUSED_BY {priority:1}]->(c_m_14) 

MERGE (s_t04:Symptom {uid: 'S_TRANS_N04'}) SET s_t04.name='变压器输出电压异常', s_t04.source_doc='船舶电气设备维护与修理', s_t04.source_page='第五章第六节', s_t04.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_TRANSFORMER'}) MERGE (s_t04)-[:BELONGS_TO]->(e)
MERGE (s_t04)-[:CAUSED_BY {priority:1}]->(c_t_01) MERGE (s_t04)-[:CAUSED_BY {priority:2}]->(c_t_04)

// ==================== 断路器 ====================

MERGE (c_b_01:Cause {uid: 'C_BREAK_001'}) SET c_b_01.name='欠压脱扣器线圈烧毁', c_b_01.check_method='measure', c_b_01.check_time='3分钟', c_b_01.created_at=timestamp()
MERGE (c_b_02:Cause {uid: 'C_BREAK_002'}) SET c_b_02.name='合闸机构机械故障', c_b_02.check_method='visual', c_b_02.check_time='3分钟', c_b_02.created_at=timestamp()
MERGE (c_b_03:Cause {uid: 'C_BREAK_003'}) SET c_b_03.name='过电流脱扣器误整定', c_b_03.check_method='measure', c_b_03.check_time='5分钟', c_b_03.created_at=timestamp()
MERGE (c_b_04:Cause {uid: 'C_BREAK_004'}) SET c_b_04.name='接线端过热氧化', c_b_04.check_method='visual', c_b_04.check_time='1分钟', c_b_04.created_at=timestamp()

MERGE (s_b01:Symptom {uid: 'S_BREAK_N01'}) SET s_b01.name='不能合闸', s_b01.source_doc='船舶电气设备维护与修理', s_b01.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_BREAKER'}) MERGE (s_b01)-[:BELONGS_TO]->(e)
MERGE (s_b01)-[:CAUSED_BY {priority:1}]->(c_b_01) MERGE (s_b01)-[:CAUSED_BY {priority:2}]->(c_b_02) MERGE (s_b01)-[:CAUSED_BY {priority:3}]->(c_voltage_low)

MERGE (s_b02:Symptom {uid: 'S_BREAK_N02'}) SET s_b02.name='误跳闸', s_b02.source_doc='船舶电气设备维护与修理', s_b02.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_BREAKER'}) MERGE (s_b02)-[:BELONGS_TO]->(e)
MERGE (s_b02)-[:CAUSED_BY {priority:1}]->(c_b_03) MERGE (s_b02)-[:CAUSED_BY {priority:2}]->(c_m_15)

MERGE (s_b03:Symptom {uid: 'S_BREAK_N03'}) SET s_b03.name='断路器过热', s_b03.source_doc='船舶电气设备维护与修理', s_b03.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_BREAKER'}) MERGE (s_b03)-[:BELONGS_TO]->(e)
MERGE (s_b03)-[:CAUSED_BY {priority:1}]->(c_b_04) MERGE (s_b03)-[:CAUSED_BY {priority:2}]->(c_m_13)

// ==================== 起货机电气系统 ====================

MERGE (c_w_01:Cause {uid: 'C_WINCH_001'}) SET c_w_01.name='主令控制器触点接触不良', c_w_01.check_method='visual', c_w_01.check_time='2分钟', c_w_01.created_at=timestamp()
MERGE (c_w_02:Cause {uid: 'C_WINCH_002'}) SET c_w_02.name='制动接触器线圈烧毁', c_w_02.check_method='measure', c_w_02.check_time='3分钟', c_w_02.created_at=timestamp()
MERGE (c_w_03:Cause {uid: 'C_WINCH_003'}) SET c_w_03.name='制动器摩擦片过度磨损', c_w_03.check_method='visual', c_w_03.check_time='2分钟', c_w_03.created_at=timestamp()
MERGE (c_w_04:Cause {uid: 'C_WINCH_004'}) SET c_w_04.name='限位开关故障', c_w_04.check_method='measure', c_w_04.check_time='2分钟', c_w_04.created_at=timestamp()
MERGE (c_w_05:Cause {uid: 'C_WINCH_005'}) SET c_w_05.name='调速电阻烧断', c_w_05.check_method='measure', c_w_05.check_time='3分钟', c_w_05.created_at=timestamp()

MERGE (s_w01:Symptom {uid: 'S_WINCH_N01'}) SET s_w01.name='起货机不能起动', s_w01.source_doc='船舶电气设备维护与修理', s_w01.source_page='第六章第四节', s_w01.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_WINCH'}) MERGE (s_w01)-[:BELONGS_TO]->(e)
MERGE (s_w01)-[:CAUSED_BY {priority:1}]->(c_w_01) MERGE (s_w01)-[:CAUSED_BY {priority:2}]->(c_m_20) MERGE (s_w01)-[:CAUSED_BY {priority:3}]->(c_w_04)

MERGE (s_w02:Symptom {uid: 'S_WINCH_N02'}) SET s_w02.name='起货机制动失灵', s_w02.source_doc='船舶电气设备维护与修理', s_w02.source_page='第六章第四节', s_w02.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_WINCH'}) MERGE (s_w02)-[:BELONGS_TO]->(e)
MERGE (s_w02)-[:CAUSED_BY {priority:1}]->(c_w_02) MERGE (s_w02)-[:CAUSED_BY {priority:2}]->(c_w_03)

MERGE (s_w03:Symptom {uid: 'S_WINCH_N03'}) SET s_w03.name='起货机不能调速', s_w03.source_doc='船舶电气设备维护与修理', s_w03.source_page='第六章第四节', s_w03.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_WINCH'}) MERGE (s_w03)-[:BELONGS_TO]->(e)
MERGE (s_w03)-[:CAUSED_BY {priority:1}]->(c_w_05) MERGE (s_w03)-[:CAUSED_BY {priority:2}]->(c_w_01)

// ==================== 锚机/绞缆机 ====================

MERGE (c_a_01:Cause {uid: 'C_ANCH_001'}) SET c_a_01.name='液压系统压力不足', c_a_01.check_method='measure', c_a_01.check_time='3分钟', c_a_01.created_at=timestamp()
MERGE (c_a_02:Cause {uid: 'C_ANCH_002'}) SET c_a_02.name='电磁阀故障', c_a_02.check_method='measure', c_a_02.check_time='5分钟', c_a_02.created_at=timestamp()
MERGE (c_a_03:Cause {uid: 'C_ANCH_003'}) SET c_a_03.name='过载保护动作', c_a_03.check_method='visual', c_a_03.check_time='1分钟', c_a_03.created_at=timestamp()

MERGE (s_a01:Symptom {uid: 'S_ANCH_N01'}) SET s_a01.name='锚机不能起动', s_a01.source_doc='船舶电气设备维护与修理', s_a01.source_page='第六章第五节', s_a01.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_ANCHOR'}) MERGE (s_a01)-[:BELONGS_TO]->(e)
MERGE (s_a01)-[:CAUSED_BY {priority:1}]->(c_m_01) MERGE (s_a01)-[:CAUSED_BY {priority:2}]->(c_a_01) MERGE (s_a01)-[:CAUSED_BY {priority:3}]->(c_a_03)

MERGE (s_a02:Symptom {uid: 'S_ANCH_N02'}) SET s_a02.name='锚机运行无力', s_a02.source_doc='船舶电气设备维护与修理', s_a02.source_page='第六章第五节', s_a02.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_ANCHOR'}) MERGE (s_a02)-[:BELONGS_TO]->(e)
MERGE (s_a02)-[:CAUSED_BY {priority:1}]->(c_a_01) MERGE (s_a02)-[:CAUSED_BY {priority:2}]->(c_m_13)

MERGE (s_a03:Symptom {uid: 'S_ANCH_N03'}) SET s_a03.name='锚机异常噪声', s_a03.source_doc='船舶电气设备维护与修理', s_a03.source_page='第六章第五节', s_a03.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_ANCHOR'}) MERGE (s_a03)-[:BELONGS_TO]->(e)
MERGE (s_a03)-[:CAUSED_BY {priority:1}]->(c_m_06) MERGE (s_a03)-[:CAUSED_BY {priority:2}]->(c_a_02)

// ==================== 舵机 ====================

MERGE (c_st_01:Cause {uid: 'C_STEER_001'}) SET c_st_01.name='伺服电机故障', c_st_01.check_method='measure', c_st_01.check_time='5分钟', c_st_01.created_at=timestamp()
MERGE (c_st_02:Cause {uid: 'C_STEER_002'}) SET c_st_02.name='反馈电位计故障', c_st_02.check_method='measure', c_st_02.check_time='5分钟', c_st_02.created_at=timestamp()
MERGE (c_st_03:Cause {uid: 'C_STEER_003'}) SET c_st_03.name='液压泵电机过载', c_st_03.check_method='measure', c_st_03.check_time='3分钟', c_st_03.created_at=timestamp()

MERGE (s_st01:Symptom {uid: 'S_STEER_N01'}) SET s_st01.name='舵机不动作', s_st01.source_doc='船舶电气设备维护与修理', s_st01.source_page='第六章第六节', s_st01.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_STEER'}) MERGE (s_st01)-[:BELONGS_TO]->(e)
MERGE (s_st01)-[:CAUSED_BY {priority:1}]->(c_st_01) MERGE (s_st01)-[:CAUSED_BY {priority:2}]->(c_m_01) MERGE (s_st01)-[:CAUSED_BY {priority:3}]->(c_m_20)

MERGE (s_st02:Symptom {uid: 'S_STEER_N02'}) SET s_st02.name='舵角不准', s_st02.source_doc='船舶电气设备维护与修理', s_st02.source_page='第六章第六节', s_st02.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_STEER'}) MERGE (s_st02)-[:BELONGS_TO]->(e)
MERGE (s_st02)-[:CAUSED_BY {priority:1}]->(c_st_02)

MERGE (s_st03:Symptom {uid: 'S_STEER_N03'}) SET s_st03.name='舵机过热跳闸', s_st03.source_doc='船舶电气设备维护与修理', s_st03.source_page='第六章第六节', s_st03.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_STEER'}) MERGE (s_st03)-[:BELONGS_TO]->(e)
MERGE (s_st03)-[:CAUSED_BY {priority:1}]->(c_st_03) MERGE (s_st03)-[:CAUSED_BY {priority:2}]->(c_m_13)

// ==================== 辅锅炉 ====================

MERGE (c_bo_01:Cause {uid: 'C_BOIL_001'}) SET c_bo_01.name='点火变压器故障', c_bo_01.check_method='measure', c_bo_01.check_time='5分钟', c_bo_01.created_at=timestamp()
MERGE (c_bo_02:Cause {uid: 'C_BOIL_002'}) SET c_bo_02.name='火焰探测器脏污', c_bo_02.check_method='visual', c_bo_02.check_time='1分钟', c_bo_02.created_at=timestamp()
MERGE (c_bo_03:Cause {uid: 'C_BOIL_003'}) SET c_bo_03.name='水位电极故障', c_bo_03.check_method='measure', c_bo_03.check_time='3分钟', c_bo_03.created_at=timestamp()
MERGE (c_bo_04:Cause {uid: 'C_BOIL_004'}) SET c_bo_04.name='燃油电磁阀故障', c_bo_04.check_method='measure', c_bo_04.check_time='3分钟', c_bo_04.created_at=timestamp()
MERGE (c_bo_05:Cause {uid: 'C_BOIL_005'}) SET c_bo_05.name='风门执行器故障', c_bo_05.check_method='visual', c_bo_05.check_time='3分钟', c_bo_05.created_at=timestamp()

MERGE (s_bo01:Symptom {uid: 'S_BOIL_N01'}) SET s_bo01.name='锅炉点火失败', s_bo01.source_doc='船舶电气设备维护与修理', s_bo01.source_page='第六章第七节', s_bo01.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_BOILER'}) MERGE (s_bo01)-[:BELONGS_TO]->(e)
MERGE (s_bo01)-[:CAUSED_BY {priority:1}]->(c_bo_01) MERGE (s_bo01)-[:CAUSED_BY {priority:2}]->(c_bo_02) MERGE (s_bo01)-[:CAUSED_BY {priority:3}]->(c_bo_04)

MERGE (s_bo02:Symptom {uid: 'S_BOIL_N02'}) SET s_bo02.name='锅炉熄火报警', s_bo02.source_doc='船舶电气设备维护与修理', s_bo02.source_page='第六章第七节', s_bo02.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_BOILER'}) MERGE (s_bo02)-[:BELONGS_TO]->(e)
MERGE (s_bo02)-[:CAUSED_BY {priority:1}]->(c_bo_02) MERGE (s_bo02)-[:CAUSED_BY {priority:2}]->(c_bo_05)

MERGE (s_bo03:Symptom {uid: 'S_BOIL_N03'}) SET s_bo03.name='锅炉水位控制失灵', s_bo03.source_doc='船舶电气设备维护与修理', s_bo03.source_page='第六章第七节', s_bo03.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_BOILER'}) MERGE (s_bo03)-[:BELONGS_TO]->(e)
MERGE (s_bo03)-[:CAUSED_BY {priority:1}]->(c_bo_03)

// ==================== 配电装置 ====================

MERGE (c_pd_01:Cause {uid: 'C_PDIST_001'}) SET c_pd_01.name='主开关储能机构故障', c_pd_01.check_method='visual', c_pd_01.check_time='3分钟', c_pd_01.created_at=timestamp()
MERGE (c_pd_02:Cause {uid: 'C_PDIST_002'}) SET c_pd_02.name='逆功率继电器误动', c_pd_02.check_method='measure', c_pd_02.check_time='5分钟', c_pd_02.created_at=timestamp()
MERGE (c_pd_03:Cause {uid: 'C_PDIST_003'}) SET c_pd_03.name='汇流排连接螺栓松动', c_pd_03.check_method='visual', c_pd_03.check_time='2分钟', c_pd_03.created_at=timestamp()

MERGE (s_pd01:Symptom {uid: 'S_PDIST_N01'}) SET s_pd01.name='主开关不能合闸', s_pd01.source_doc='船舶电气设备维护与修理', s_pd01.source_page='第十一章第三节', s_pd01.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_PDIST'}) MERGE (s_pd01)-[:BELONGS_TO]->(e)
MERGE (s_pd01)-[:CAUSED_BY {priority:1}]->(c_pd_01) MERGE (s_pd01)-[:CAUSED_BY {priority:2}]->(c_b_01)

MERGE (s_pd02:Symptom {uid: 'S_PDIST_N02'}) SET s_pd02.name='配电板电压波动', s_pd02.source_doc='船舶电气设备维护与修理', s_pd02.source_page='第十一章第三节', s_pd02.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_PDIST'}) MERGE (s_pd02)-[:BELONGS_TO]->(e)
MERGE (s_pd02)-[:CAUSED_BY {priority:1}]->(c_g_07) MERGE (s_pd02)-[:CAUSED_BY {priority:2}]->(c_pd_03)

MERGE (s_pd03:Symptom {uid: 'S_PDIST_N03'}) SET s_pd03.name='岸电/船电切换失败', s_pd03.source_doc='船舶电气设备维护与修理', s_pd03.source_page='第十一章第三节', s_pd03.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_PDIST'}) MERGE (s_pd03)-[:BELONGS_TO]->(e)
MERGE (s_pd03)-[:CAUSED_BY {priority:1}]->(c_pd_02) MERGE (s_pd03)-[:CAUSED_BY {priority:2}]->(c_m_19)

// ==================== 报警系统 ====================

MERGE (c_al_01:Cause {uid: 'C_ALARM_001'}) SET c_al_01.name='探测器污染或老化', c_al_01.check_method='visual', c_al_01.check_time='2分钟', c_al_01.created_at=timestamp()
MERGE (c_al_02:Cause {uid: 'C_ALARM_002'}) SET c_al_02.name='报警回路断线', c_al_02.check_method='measure', c_al_02.check_time='5分钟', c_al_02.created_at=timestamp()
MERGE (c_al_03:Cause {uid: 'C_ALARM_003'}) SET c_al_03.name='报警控制器电源故障', c_al_03.check_method='measure', c_al_03.check_time='2分钟', c_al_03.created_at=timestamp()
MERGE (c_al_04:Cause {uid: 'C_ALARM_004'}) SET c_al_04.name='传感器零点漂移', c_al_04.check_method='measure', c_al_04.check_time='5分钟', c_al_04.created_at=timestamp()

MERGE (s_al01:Symptom {uid: 'S_ALARM_N01'}) SET s_al01.name='火灾报警误报', s_al01.source_doc='船舶电气设备维护与修理', s_al01.source_page='第七章第二节', s_al01.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_FIRE_ALARM'}) MERGE (s_al01)-[:BELONGS_TO]->(e)
MERGE (s_al01)-[:CAUSED_BY {priority:1}]->(c_al_01) MERGE (s_al01)-[:CAUSED_BY {priority:2}]->(c_m_14)

MERGE (s_al02:Symptom {uid: 'S_ALARM_N02'}) SET s_al02.name='报警系统不工作', s_al02.source_doc='船舶电气设备维护与修理', s_al02.source_page='第七章第二节', s_al02.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_FIRE_ALARM'}) MERGE (s_al02)-[:BELONGS_TO]->(e)
MERGE (s_al02)-[:CAUSED_BY {priority:1}]->(c_al_03) MERGE (s_al02)-[:CAUSED_BY {priority:2}]->(c_al_02)

MERGE (s_al03:Symptom {uid: 'S_MON_N01'}) SET s_al03.name='监测数据异常跳变', s_al03.source_doc='船舶电气设备维护与修理', s_al03.source_page='第七章第四节', s_al03.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_MONITOR'}) MERGE (s_al03)-[:BELONGS_TO]->(e)
MERGE (s_al03)-[:CAUSED_BY {priority:1}]->(c_al_04) MERGE (s_al03)-[:CAUSED_BY {priority:2}]->(c_m_15)

// ==================== 公共 Precautions ====================

MERGE (p_ex_01:Precaution {uid: 'P_EX_001'}) SET p_ex_01.name='断电挂牌后方可操作', p_ex_01.created_at=timestamp()
MERGE (p_ex_02:Precaution {uid: 'P_EX_002'}) SET p_ex_02.name='使用绝缘工具', p_ex_02.created_at=timestamp()
MERGE (p_ex_03:Precaution {uid: 'P_EX_003'}) SET p_ex_03.name='测量前确认仪表量程正确', p_ex_03.created_at=timestamp()
MERGE (p_ex_04:Precaution {uid: 'P_EX_004'}) SET p_ex_04.name='更换元件时确保型号规格一致', p_ex_04.created_at=timestamp()
MERGE (p_ex_05:Precaution {uid: 'P_EX_005'}) SET p_ex_05.name='做好维修记录', p_ex_05.created_at=timestamp()
MERGE (p_ex_06:Precaution {uid: 'P_EX_006'}) SET p_ex_06.name='电容放电2-3分钟后再操作', p_ex_06.created_at=timestamp()
MERGE (p_ex_07:Precaution {uid: 'P_EX_007'}) SET p_ex_07.name='注意高压危险', p_ex_07.created_at=timestamp()

// ==================== 公共 Tools ====================
MERGE (t_ex_01:Tool {uid: 'T_EX_001'}) SET t_ex_01.name='万用表', t_ex_01.created_at=timestamp()
MERGE (t_ex_02:Tool {uid: 'T_EX_002'}) SET t_ex_02.name='绝缘电阻表(摇表)', t_ex_02.created_at=timestamp()
MERGE (t_ex_03:Tool {uid: 'T_EX_003'}) SET t_ex_03.name='钳形电流表', t_ex_03.created_at=timestamp()
MERGE (t_ex_04:Tool {uid: 'T_EX_004'}) SET t_ex_04.name='短路侦察器', t_ex_04.created_at=timestamp()
MERGE (t_ex_05:Tool {uid: 'T_EX_005'}) SET t_ex_05.name='砂纸(0#)', t_ex_05.created_at=timestamp()
MERGE (t_ex_06:Tool {uid: 'T_EX_006'}) SET t_ex_06.name='千分尺', t_ex_06.created_at=timestamp()
MERGE (t_ex_07:Tool {uid: 'T_EX_007'}) SET t_ex_07.name='套筒扳手组', t_ex_07.created_at=timestamp()
MERGE (t_ex_08:Tool {uid: 'T_EX_008'}) SET t_ex_08.name='电烙铁', t_ex_08.created_at=timestamp()
MERGE (t_ex_09:Tool {uid: 'T_EX_009'}) SET t_ex_09.name='拉马(轴承拆卸)', t_ex_09.created_at=timestamp()
MERGE (t_ex_10:Tool {uid: 'T_EX_010'}) SET t_ex_10.name='塞尺', t_ex_10.created_at=timestamp()
