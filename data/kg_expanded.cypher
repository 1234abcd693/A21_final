// A21 KG Expanded Data
// Triples: 69

// --- 接触器: 不能吸合 ---
MERGE (s_EXP_1001:Symptom {uid: 'EXP_1001'}) SET s_EXP_1001.name='接触器不能吸合', s_EXP_1001.source_doc='船舶电气设备维护与修理', s_EXP_1001.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_CONTACTOR'}) MERGE (s_EXP_1001)-[:BELONGS_TO]->(e)
MERGE (c_C_5000:Cause {uid: 'C_5000'}) SET c_C_5000.name='电源电压过低', c_C_5000.created_at=timestamp()
MERGE (s_EXP_1001)-[:CAUSED_BY {priority: 1}]->(c_C_5000)
MERGE (c_C_5001:Cause {uid: 'C_5001'}) SET c_C_5001.name='线圈断路', c_C_5001.created_at=timestamp()
MERGE (s_EXP_1001)-[:CAUSED_BY {priority: 2}]->(c_C_5001)
MERGE (c_C_5002:Cause {uid: 'C_5002'}) SET c_C_5002.name='转轴锈蚀', c_C_5002.created_at=timestamp()
MERGE (s_EXP_1001)-[:CAUSED_BY {priority: 3}]->(c_C_5002)
MERGE (c_C_5003:Cause {uid: 'C_5003'}) SET c_C_5003.name='弹簧反力过大', c_C_5003.created_at=timestamp()
MERGE (s_EXP_1001)-[:CAUSED_BY {priority: 4}]->(c_C_5003)
MERGE (c_C_5004:Cause {uid: 'C_5004'}) SET c_C_5004.name='弹簧失效', c_C_5004.created_at=timestamp()
MERGE (s_EXP_1001)-[:CAUSED_BY {priority: 5}]->(c_C_5004)
MERGE (st_ST_6000:Step {uid: 'ST_6000'}) SET st_ST_6000.name='更换线圈', st_ST_6000.created_at=timestamp()
MERGE (c_C_5000)-[:FIXED_BY]->(st_ST_6000)
MERGE (st_ST_6001:Step {uid: 'ST_6001'}) SET st_ST_6001.name='调整衔铁气隙', st_ST_6001.created_at=timestamp()
MERGE (st_ST_6000)-[:NEXT_STEP]->(st_ST_6001)

// --- 接触器: 噪声大 ---
MERGE (s_EXP_1005:Symptom {uid: 'EXP_1005'}) SET s_EXP_1005.name='接触器噪声大', s_EXP_1005.source_doc='船舶电气设备维护与修理', s_EXP_1005.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_CONTACTOR'}) MERGE (s_EXP_1005)-[:BELONGS_TO]->(e)
MERGE (c_C_5005:Cause {uid: 'C_5005'}) SET c_C_5005.name='接触不良', c_C_5005.created_at=timestamp()
MERGE (s_EXP_1005)-[:CAUSED_BY {priority: 1}]->(c_C_5005)
MERGE (c_C_5006:Cause {uid: 'C_5006'}) SET c_C_5006.name='触头接触不良', c_C_5006.created_at=timestamp()
MERGE (s_EXP_1005)-[:CAUSED_BY {priority: 2}]->(c_C_5006)
MERGE (c_C_5007:Cause {uid: 'C_5007'}) SET c_C_5007.name='短路环断裂', c_C_5007.created_at=timestamp()
MERGE (s_EXP_1005)-[:CAUSED_BY {priority: 3}]->(c_C_5007)
MERGE (c_C_5008:Cause {uid: 'C_5008'}) SET c_C_5008.name='机械卡阻', c_C_5008.created_at=timestamp()
MERGE (s_EXP_1005)-[:CAUSED_BY {priority: 4}]->(c_C_5008)
MERGE (c_C_5009:Cause {uid: 'C_5009'}) SET c_C_5009.name='衔铁歪斜', c_C_5009.created_at=timestamp()
MERGE (s_EXP_1005)-[:CAUSED_BY {priority: 5}]->(c_C_5009)
MERGE (c_C_5005)-[:FIXED_BY]->(st_ST_6000)
MERGE (st_ST_6002:Step {uid: 'ST_6002'}) SET st_ST_6002.name='调整触头压力', st_ST_6002.created_at=timestamp()
MERGE (st_ST_6000)-[:NEXT_STEP]->(st_ST_6002)
MERGE (st_ST_6003:Step {uid: 'ST_6003'}) SET st_ST_6003.name='更换触头', st_ST_6003.created_at=timestamp()
MERGE (st_ST_6002)-[:NEXT_STEP]->(st_ST_6003)
MERGE (st_ST_6004:Step {uid: 'ST_6004'}) SET st_ST_6004.name='更换短路环', st_ST_6004.created_at=timestamp()
MERGE (st_ST_6003)-[:NEXT_STEP]->(st_ST_6004)

// --- 接触器: 线圈过热 ---
MERGE (s_EXP_1009:Symptom {uid: 'EXP_1009'}) SET s_EXP_1009.name='接触器线圈过热', s_EXP_1009.source_doc='船舶电气设备维护与修理', s_EXP_1009.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_CONTACTOR'}) MERGE (s_EXP_1009)-[:BELONGS_TO]->(e)
MERGE (c_C_5010:Cause {uid: 'C_5010'}) SET c_C_5010.name='电源电压过高', c_C_5010.created_at=timestamp()
MERGE (s_EXP_1009)-[:CAUSED_BY {priority: 1}]->(c_C_5010)
MERGE (s_EXP_1009)-[:CAUSED_BY {priority: 2}]->(c_C_5005)
MERGE (s_EXP_1009)-[:CAUSED_BY {priority: 3}]->(c_C_5007)
MERGE (s_EXP_1009)-[:CAUSED_BY {priority: 4}]->(c_C_5008)
MERGE (s_EXP_1009)-[:CAUSED_BY {priority: 5}]->(c_C_5002)
MERGE (c_C_5010)-[:FIXED_BY]->(st_ST_6000)
MERGE (st_ST_6000)-[:NEXT_STEP]->(st_ST_6003)
MERGE (st_ST_6003)-[:NEXT_STEP]->(st_ST_6004)
MERGE (st_ST_6005:Step {uid: 'ST_6005'}) SET st_ST_6005.name='校正衔铁位置', st_ST_6005.created_at=timestamp()
MERGE (st_ST_6004)-[:NEXT_STEP]->(st_ST_6005)

// --- 接触器: 不释放 ---
MERGE (s_EXP_1011:Symptom {uid: 'EXP_1011'}) SET s_EXP_1011.name='接触器不释放', s_EXP_1011.source_doc='船舶电气设备维护与修理', s_EXP_1011.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_CONTACTOR'}) MERGE (s_EXP_1011)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1011)-[:CAUSED_BY {priority: 1}]->(c_C_5010)
MERGE (s_EXP_1011)-[:CAUSED_BY {priority: 2}]->(c_C_5001)
MERGE (s_EXP_1011)-[:CAUSED_BY {priority: 3}]->(c_C_5008)
MERGE (s_EXP_1011)-[:CAUSED_BY {priority: 4}]->(c_C_5002)
MERGE (s_EXP_1011)-[:CAUSED_BY {priority: 5}]->(c_C_5004)
MERGE (c_C_5010)-[:FIXED_BY]->(st_ST_6000)
MERGE (st_ST_6000)-[:NEXT_STEP]->(st_ST_6003)

// --- 接触器: 触头熔焊 ---
MERGE (s_EXP_1014:Symptom {uid: 'EXP_1014'}) SET s_EXP_1014.name='接触器触头熔焊', s_EXP_1014.source_doc='船舶电气设备维护与修理', s_EXP_1014.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_CONTACTOR'}) MERGE (s_EXP_1014)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1014)-[:CAUSED_BY {priority: 1}]->(c_C_5010)
MERGE (s_EXP_1014)-[:CAUSED_BY {priority: 2}]->(c_C_5001)
MERGE (s_EXP_1014)-[:CAUSED_BY {priority: 3}]->(c_C_5005)
MERGE (s_EXP_1014)-[:CAUSED_BY {priority: 4}]->(c_C_5007)
MERGE (s_EXP_1014)-[:CAUSED_BY {priority: 5}]->(c_C_5008)
MERGE (c_C_5010)-[:FIXED_BY]->(st_ST_6000)
MERGE (st_ST_6000)-[:NEXT_STEP]->(st_ST_6003)

// --- 接触器: 触头过热 ---
MERGE (s_EXP_1015:Symptom {uid: 'EXP_1015'}) SET s_EXP_1015.name='接触器触头过热', s_EXP_1015.source_doc='船舶电气设备维护与修理', s_EXP_1015.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_CONTACTOR'}) MERGE (s_EXP_1015)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1015)-[:CAUSED_BY {priority: 1}]->(c_C_5001)
MERGE (s_EXP_1015)-[:CAUSED_BY {priority: 2}]->(c_C_5005)
MERGE (st_ST_6006:Step {uid: 'ST_6006'}) SET st_ST_6006.name='检查短路环是否断裂', st_ST_6006.created_at=timestamp()
MERGE (c_C_5001)-[:FIXED_BY]->(st_ST_6006)
MERGE (st_ST_6006)-[:NEXT_STEP]->(st_ST_6004)

// --- 接触器: 触头磨损 ---
MERGE (s_EXP_1017:Symptom {uid: 'EXP_1017'}) SET s_EXP_1017.name='接触器触头磨损', s_EXP_1017.source_doc='船舶电气设备维护与修理', s_EXP_1017.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_CONTACTOR'}) MERGE (s_EXP_1017)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1017)-[:CAUSED_BY {priority: 1}]->(c_C_5005)
MERGE (s_EXP_1017)-[:CAUSED_BY {priority: 2}]->(c_C_5006)
MERGE (c_C_5011:Cause {uid: 'C_5011'}) SET c_C_5011.name='环境温度过高', c_C_5011.created_at=timestamp()
MERGE (s_EXP_1017)-[:CAUSED_BY {priority: 3}]->(c_C_5011)
MERGE (c_C_5005)-[:FIXED_BY]->(st_ST_6003)
MERGE (st_ST_6007:Step {uid: 'ST_6007'}) SET st_ST_6007.name='调整弹簧压力', st_ST_6007.created_at=timestamp()
MERGE (st_ST_6003)-[:NEXT_STEP]->(st_ST_6007)

// --- 断路器: 不能合闸 ---
MERGE (s_EXP_1019:Symptom {uid: 'EXP_1019'}) SET s_EXP_1019.name='断路器不能合闸', s_EXP_1019.source_doc='船舶电气设备维护与修理', s_EXP_1019.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_BREAKER'}) MERGE (s_EXP_1019)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1019)-[:CAUSED_BY {priority: 1}]->(c_C_5005)

// --- 断路器: 不能分闸 ---
MERGE (s_EXP_1020:Symptom {uid: 'EXP_1020'}) SET s_EXP_1020.name='断路器不能分闸', s_EXP_1020.source_doc='船舶电气设备维护与修理', s_EXP_1020.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_BREAKER'}) MERGE (s_EXP_1020)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1020)-[:CAUSED_BY {priority: 1}]->(c_C_5005)

// --- 断路器: 误跳闸 ---
MERGE (s_EXP_1021:Symptom {uid: 'EXP_1021'}) SET s_EXP_1021.name='断路器误跳闸', s_EXP_1021.source_doc='船舶电气设备维护与修理', s_EXP_1021.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_BREAKER'}) MERGE (s_EXP_1021)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1021)-[:CAUSED_BY {priority: 1}]->(c_C_5005)
MERGE (c_C_5005)-[:FIXED_BY]->(st_ST_6002)
MERGE (st_ST_6002)-[:NEXT_STEP]->(st_ST_6003)

// --- 断路器: 过热 ---
MERGE (s_EXP_1022:Symptom {uid: 'EXP_1022'}) SET s_EXP_1022.name='断路器过热', s_EXP_1022.source_doc='船舶电气设备维护与修理', s_EXP_1022.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_BREAKER'}) MERGE (s_EXP_1022)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1022)-[:CAUSED_BY {priority: 1}]->(c_C_5005)

// --- 热继电器: 误动作 ---
MERGE (s_EXP_1024:Symptom {uid: 'EXP_1024'}) SET s_EXP_1024.name='热继电器误动作', s_EXP_1024.source_doc='船舶电气设备维护与修理', s_EXP_1024.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_THERMAL_RELAY'}) MERGE (s_EXP_1024)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1024)-[:CAUSED_BY {priority: 1}]->(c_C_5005)
MERGE (c_C_5005)-[:FIXED_BY]->(st_ST_6002)
MERGE (st_ST_6002)-[:NEXT_STEP]->(st_ST_6003)

// --- 热继电器: 不动作 ---
MERGE (s_EXP_1025:Symptom {uid: 'EXP_1025'}) SET s_EXP_1025.name='热继电器不动作', s_EXP_1025.source_doc='船舶电气设备维护与修理', s_EXP_1025.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_THERMAL_RELAY'}) MERGE (s_EXP_1025)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1025)-[:CAUSED_BY {priority: 1}]->(c_C_5005)
MERGE (s_EXP_1025)-[:CAUSED_BY {priority: 2}]->(c_C_5006)

// --- 电动机: 不能起动 ---
MERGE (s_EXP_1026:Symptom {uid: 'EXP_1026'}) SET s_EXP_1026.name='电动机不能起动', s_EXP_1026.source_doc='船舶电气设备维护与修理', s_EXP_1026.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_ASYNCH_MOTOR'}) MERGE (s_EXP_1026)-[:BELONGS_TO]->(e)
MERGE (c_C_5012:Cause {uid: 'C_5012'}) SET c_C_5012.name='长期过载', c_C_5012.created_at=timestamp()
MERGE (s_EXP_1026)-[:CAUSED_BY {priority: 1}]->(c_C_5012)

// --- 电动机: 过热 ---
MERGE (s_EXP_1027:Symptom {uid: 'EXP_1027'}) SET s_EXP_1027.name='电动机过热', s_EXP_1027.source_doc='船舶电气设备维护与修理', s_EXP_1027.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_ASYNCH_MOTOR'}) MERGE (s_EXP_1027)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1027)-[:CAUSED_BY {priority: 1}]->(c_C_5005)

// --- 电动机: 振动异常 ---
MERGE (s_EXP_1033:Symptom {uid: 'EXP_1033'}) SET s_EXP_1033.name='电动机振动异常', s_EXP_1033.source_doc='船舶电气设备维护与修理', s_EXP_1033.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_ASYNCH_MOTOR'}) MERGE (s_EXP_1033)-[:BELONGS_TO]->(e)
MERGE (c_C_5013:Cause {uid: 'C_5013'}) SET c_C_5013.name='绕组断路', c_C_5013.created_at=timestamp()
MERGE (s_EXP_1033)-[:CAUSED_BY {priority: 1}]->(c_C_5013)
MERGE (c_C_5014:Cause {uid: 'C_5014'}) SET c_C_5014.name='轴承损坏', c_C_5014.created_at=timestamp()
MERGE (s_EXP_1033)-[:CAUSED_BY {priority: 2}]->(c_C_5014)

// --- 电动机: 转速异常 ---
MERGE (s_EXP_1035:Symptom {uid: 'EXP_1035'}) SET s_EXP_1035.name='电动机转速异常', s_EXP_1035.source_doc='船舶电气设备维护与修理', s_EXP_1035.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_ASYNCH_MOTOR'}) MERGE (s_EXP_1035)-[:BELONGS_TO]->(e)
MERGE (c_C_5015:Cause {uid: 'C_5015'}) SET c_C_5015.name='线圈匝间短路', c_C_5015.created_at=timestamp()
MERGE (s_EXP_1035)-[:CAUSED_BY {priority: 1}]->(c_C_5015)
MERGE (c_C_5016:Cause {uid: 'C_5016'}) SET c_C_5016.name='绕组短路', c_C_5016.created_at=timestamp()
MERGE (s_EXP_1035)-[:CAUSED_BY {priority: 2}]->(c_C_5016)
MERGE (s_EXP_1035)-[:CAUSED_BY {priority: 3}]->(c_C_5005)
MERGE (c_C_5017:Cause {uid: 'C_5017'}) SET c_C_5017.name='堵转', c_C_5017.created_at=timestamp()
MERGE (s_EXP_1035)-[:CAUSED_BY {priority: 4}]->(c_C_5017)
MERGE (s_EXP_1035)-[:CAUSED_BY {priority: 5}]->(c_C_5012)

// --- 电动机: 绝缘降低 ---
MERGE (s_EXP_1037:Symptom {uid: 'EXP_1037'}) SET s_EXP_1037.name='电动机绝缘降低', s_EXP_1037.source_doc='船舶电气设备维护与修理', s_EXP_1037.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_ASYNCH_MOTOR'}) MERGE (s_EXP_1037)-[:BELONGS_TO]->(e)
MERGE (c_C_5018:Cause {uid: 'C_5018'}) SET c_C_5018.name='绕组受潮', c_C_5018.created_at=timestamp()
MERGE (s_EXP_1037)-[:CAUSED_BY {priority: 1}]->(c_C_5018)
MERGE (c_C_5019:Cause {uid: 'C_5019'}) SET c_C_5019.name='绝缘老化', c_C_5019.created_at=timestamp()
MERGE (s_EXP_1037)-[:CAUSED_BY {priority: 2}]->(c_C_5019)
MERGE (c_C_5020:Cause {uid: 'C_5020'}) SET c_C_5020.name='绝缘损坏', c_C_5020.created_at=timestamp()
MERGE (s_EXP_1037)-[:CAUSED_BY {priority: 3}]->(c_C_5020)
MERGE (c_C_5021:Cause {uid: 'C_5021'}) SET c_C_5021.name='绝缘电阻降低', c_C_5021.created_at=timestamp()
MERGE (s_EXP_1037)-[:CAUSED_BY {priority: 4}]->(c_C_5021)

// --- 电动机: 单相运行 ---
MERGE (s_EXP_1039:Symptom {uid: 'EXP_1039'}) SET s_EXP_1039.name='电动机单相运行', s_EXP_1039.source_doc='船舶电气设备维护与修理', s_EXP_1039.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_ASYNCH_MOTOR'}) MERGE (s_EXP_1039)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1039)-[:CAUSED_BY {priority: 1}]->(c_C_5005)
MERGE (s_EXP_1039)-[:CAUSED_BY {priority: 2}]->(c_C_5006)

// --- 发电机: 不能建压 ---
MERGE (s_EXP_1042:Symptom {uid: 'EXP_1042'}) SET s_EXP_1042.name='发电机不能建压', s_EXP_1042.source_doc='船舶电气设备维护与修理', s_EXP_1042.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_GENERATOR'}) MERGE (s_EXP_1042)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1042)-[:CAUSED_BY {priority: 1}]->(c_C_5015)
MERGE (s_EXP_1042)-[:CAUSED_BY {priority: 2}]->(c_C_5016)
MERGE (s_EXP_1042)-[:CAUSED_BY {priority: 3}]->(c_C_5005)
MERGE (s_EXP_1042)-[:CAUSED_BY {priority: 4}]->(c_C_5017)

// --- 发电机: 电压低 ---
MERGE (s_EXP_1044:Symptom {uid: 'EXP_1044'}) SET s_EXP_1044.name='发电机电压低', s_EXP_1044.source_doc='船舶电气设备维护与修理', s_EXP_1044.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_GENERATOR'}) MERGE (s_EXP_1044)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1044)-[:CAUSED_BY {priority: 1}]->(c_C_5005)
MERGE (s_EXP_1044)-[:CAUSED_BY {priority: 2}]->(c_C_5006)
MERGE (s_EXP_1044)-[:CAUSED_BY {priority: 3}]->(c_C_5007)
MERGE (s_EXP_1044)-[:CAUSED_BY {priority: 4}]->(c_C_5008)
MERGE (s_EXP_1044)-[:CAUSED_BY {priority: 5}]->(c_C_5009)
MERGE (c_C_5005)-[:FIXED_BY]->(st_ST_6000)
MERGE (st_ST_6000)-[:NEXT_STEP]->(st_ST_6002)
MERGE (st_ST_6002)-[:NEXT_STEP]->(st_ST_6003)
MERGE (st_ST_6003)-[:NEXT_STEP]->(st_ST_6004)

// --- 发电机: 电压不稳 ---
MERGE (s_EXP_1046:Symptom {uid: 'EXP_1046'}) SET s_EXP_1046.name='发电机电压不稳', s_EXP_1046.source_doc='船舶电气设备维护与修理', s_EXP_1046.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_GENERATOR'}) MERGE (s_EXP_1046)-[:BELONGS_TO]->(e)
MERGE (c_C_5022:Cause {uid: 'C_5022'}) SET c_C_5022.name='操作频率过高', c_C_5022.created_at=timestamp()
MERGE (s_EXP_1046)-[:CAUSED_BY {priority: 1}]->(c_C_5022)
MERGE (s_EXP_1046)-[:CAUSED_BY {priority: 2}]->(c_C_5017)

// --- 发电机: 过热 ---
MERGE (s_EXP_1047:Symptom {uid: 'EXP_1047'}) SET s_EXP_1047.name='发电机过热', s_EXP_1047.source_doc='船舶电气设备维护与修理', s_EXP_1047.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_GENERATOR'}) MERGE (s_EXP_1047)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1047)-[:CAUSED_BY {priority: 1}]->(c_C_5005)

// --- 发电机: 异响 ---
MERGE (s_EXP_1051:Symptom {uid: 'EXP_1051'}) SET s_EXP_1051.name='发电机异响', s_EXP_1051.source_doc='船舶电气设备维护与修理', s_EXP_1051.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_GENERATOR'}) MERGE (s_EXP_1051)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1051)-[:CAUSED_BY {priority: 1}]->(c_C_5005)
MERGE (s_EXP_1051)-[:CAUSED_BY {priority: 2}]->(c_C_5006)
MERGE (s_EXP_1051)-[:CAUSED_BY {priority: 3}]->(c_C_5007)
MERGE (s_EXP_1051)-[:CAUSED_BY {priority: 4}]->(c_C_5008)
MERGE (s_EXP_1051)-[:CAUSED_BY {priority: 5}]->(c_C_5009)
MERGE (c_C_5005)-[:FIXED_BY]->(st_ST_6000)
MERGE (st_ST_6000)-[:NEXT_STEP]->(st_ST_6002)
MERGE (st_ST_6002)-[:NEXT_STEP]->(st_ST_6003)
MERGE (st_ST_6003)-[:NEXT_STEP]->(st_ST_6004)

// --- 变压器: 过热 ---
MERGE (s_EXP_1053:Symptom {uid: 'EXP_1053'}) SET s_EXP_1053.name='变压器过热', s_EXP_1053.source_doc='船舶电气设备维护与修理', s_EXP_1053.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_TRANSFORMER'}) MERGE (s_EXP_1053)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1053)-[:CAUSED_BY {priority: 1}]->(c_C_5005)

// --- 变压器: 噪声大 ---
MERGE (s_EXP_1058:Symptom {uid: 'EXP_1058'}) SET s_EXP_1058.name='变压器噪声大', s_EXP_1058.source_doc='船舶电气设备维护与修理', s_EXP_1058.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_TRANSFORMER'}) MERGE (s_EXP_1058)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1058)-[:CAUSED_BY {priority: 1}]->(c_C_5005)
MERGE (s_EXP_1058)-[:CAUSED_BY {priority: 2}]->(c_C_5006)
MERGE (s_EXP_1058)-[:CAUSED_BY {priority: 3}]->(c_C_5007)
MERGE (s_EXP_1058)-[:CAUSED_BY {priority: 4}]->(c_C_5008)
MERGE (s_EXP_1058)-[:CAUSED_BY {priority: 5}]->(c_C_5009)
MERGE (c_C_5005)-[:FIXED_BY]->(st_ST_6000)
MERGE (st_ST_6000)-[:NEXT_STEP]->(st_ST_6002)
MERGE (st_ST_6002)-[:NEXT_STEP]->(st_ST_6003)
MERGE (st_ST_6003)-[:NEXT_STEP]->(st_ST_6004)

// --- 变压器: 绝缘降低 ---
MERGE (s_EXP_1060:Symptom {uid: 'EXP_1060'}) SET s_EXP_1060.name='变压器绝缘降低', s_EXP_1060.source_doc='船舶电气设备维护与修理', s_EXP_1060.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_TRANSFORMER'}) MERGE (s_EXP_1060)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1060)-[:CAUSED_BY {priority: 1}]->(c_C_5018)
MERGE (s_EXP_1060)-[:CAUSED_BY {priority: 2}]->(c_C_5019)
MERGE (s_EXP_1060)-[:CAUSED_BY {priority: 3}]->(c_C_5020)
MERGE (s_EXP_1060)-[:CAUSED_BY {priority: 4}]->(c_C_5021)

// --- 变压器: 输出电压异常 ---
MERGE (s_EXP_1063:Symptom {uid: 'EXP_1063'}) SET s_EXP_1063.name='变压器输出电压异常', s_EXP_1063.source_doc='船舶电气设备维护与修理', s_EXP_1063.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_TRANSFORMER'}) MERGE (s_EXP_1063)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1063)-[:CAUSED_BY {priority: 1}]->(c_C_5005)
MERGE (s_EXP_1063)-[:CAUSED_BY {priority: 2}]->(c_C_5006)
MERGE (s_EXP_1063)-[:CAUSED_BY {priority: 3}]->(c_C_5007)
MERGE (s_EXP_1063)-[:CAUSED_BY {priority: 4}]->(c_C_5008)
MERGE (s_EXP_1063)-[:CAUSED_BY {priority: 5}]->(c_C_5009)
MERGE (c_C_5005)-[:FIXED_BY]->(st_ST_6000)
MERGE (st_ST_6000)-[:NEXT_STEP]->(st_ST_6002)
MERGE (st_ST_6002)-[:NEXT_STEP]->(st_ST_6003)
MERGE (st_ST_6003)-[:NEXT_STEP]->(st_ST_6004)

// --- 起货机: 不能起动 ---
MERGE (s_EXP_1065:Symptom {uid: 'EXP_1065'}) SET s_EXP_1065.name='起货机不能起动', s_EXP_1065.source_doc='船舶电气设备维护与修理', s_EXP_1065.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_WINCH'}) MERGE (s_EXP_1065)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1065)-[:CAUSED_BY {priority: 1}]->(c_C_5012)

// --- 配电装置: 电压异常 ---
MERGE (s_EXP_1067:Symptom {uid: 'EXP_1067'}) SET s_EXP_1067.name='配电装置电压异常', s_EXP_1067.source_doc='船舶电气设备维护与修理', s_EXP_1067.created_at=timestamp()
MATCH (e:Equipment {uid: 'E_PDIST'}) MERGE (s_EXP_1067)-[:BELONGS_TO]->(e)
MERGE (s_EXP_1067)-[:CAUSED_BY {priority: 1}]->(c_C_5017)
