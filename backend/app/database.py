"""
数据库连接和会话管理
"""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL, DB_TYPE

# 创建数据库引擎
if DB_TYPE == "sqlite":
    # SQLite配置
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite需要这个参数
        echo=False
    )
else:
    # MySQL配置
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False
    )

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


def get_db():
    """
    获取数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _column_exists(inspector, table_name: str, column_name: str) -> bool:
    """检查列是否存在"""
    try:
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in columns
    except Exception:
        return False


def _table_exists(inspector, table_name: str) -> bool:
    """检查表是否存在"""
    return table_name in inspector.get_table_names()


def init_db():
    """
    初始化数据库：创建数据库和表
    """
    try:
        if DB_TYPE == "mysql":
            # MySQL初始化逻辑
            import pymysql
            from app.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
            
            print("正在连接MySQL服务器...")
            connection = pymysql.connect(
                host=DB_HOST,
                port=int(DB_PORT),
                user=DB_USER,
                password=DB_PASSWORD,
                charset='utf8mb4'
            )
            
            try:
                with connection.cursor() as cursor:
                    # 创建数据库（如果不存在）
                    print(f"正在创建数据库 {DB_NAME}...")
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                    connection.commit()
                    print(f"数据库 {DB_NAME} 创建成功或已存在")
            finally:
                connection.close()
        else:
            # SQLite不需要创建数据库，文件会自动创建
            print("使用SQLite数据库...")
        
        # 创建所有表
        print("正在创建数据表...")
        from app.models import (
            User, SmsCode, 
            Course, CourseCategory, UserCourse, LearningProgress, SkillType,
            Banner,
            RuleContent, RuleProgress,
            ReactionTrainingRecord,
            OfflineCourse, OfflineCourseEnrollment
        )
        Base.metadata.create_all(bind=engine)
        print("数据表创建完成")
        
        # 检查并添加新列（用于数据库迁移）
        print("检查数据表结构...")
        inspector = inspect(engine)
        
        # 检查users表
        if _table_exists(inspector, 'users'):
            with engine.begin() as conn:
                # 检查并添加 reset_token 列
                if not _column_exists(inspector, 'users', 'reset_token'):
                    print("添加 reset_token 列...")
                    conn.execute(text("ALTER TABLE users ADD COLUMN reset_token VARCHAR(255) NULL"))
                
                # 检查并添加 reset_token_expires 列
                if not _column_exists(inspector, 'users', 'reset_token_expires'):
                    print("添加 reset_token_expires 列...")
                    conn.execute(text("ALTER TABLE users ADD COLUMN reset_token_expires DATETIME NULL"))
                
                # 检查并添加 phone 列
                if not _column_exists(inspector, 'users', 'phone'):
                    print("添加 phone 列...")
                    if DB_TYPE == "sqlite":
                        conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(20) NULL"))
                        # SQLite不支持在ALTER TABLE时添加UNIQUE约束，需要单独处理
                    else:
                        conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(20) NULL UNIQUE"))
                
                # 检查并添加 avatar 列
                if not _column_exists(inspector, 'users', 'avatar'):
                    print("添加 users.avatar 列...")
                    conn.execute(text("ALTER TABLE users ADD COLUMN avatar VARCHAR(500) NULL"))
                
                # 删除 email 列（如果存在且是MySQL）
                if DB_TYPE == "mysql" and _column_exists(inspector, 'users', 'email'):
                    print("删除 email 列...")
                    conn.execute(text("ALTER TABLE users DROP COLUMN email"))
        
        # 检查 sms_codes 表
        if _table_exists(inspector, 'sms_codes'):
            with engine.begin() as conn:
                if not _column_exists(inspector, 'sms_codes', 'is_used'):
                    print("添加 sms_codes.is_used 列...")
                    if DB_TYPE == "sqlite":
                        conn.execute(text("ALTER TABLE sms_codes ADD COLUMN is_used BOOLEAN DEFAULT 0"))
                    else:
                        conn.execute(text("ALTER TABLE sms_codes ADD COLUMN is_used BOOLEAN DEFAULT FALSE"))
        
        # 检查 skill_types 表
        if _table_exists(inspector, 'skill_types'):
            with engine.begin() as conn:
                columns_to_add = [
                    ('skill_type', 'VARCHAR(50) NULL'),
                    ('intro', 'TEXT NULL'),
                    ('focus_points', 'TEXT NULL'),
                    ('training_methods', 'TEXT NULL'),
                    ('tips', 'TEXT NULL'),
                    ('is_active', 'BOOLEAN DEFAULT 1' if DB_TYPE == "sqlite" else 'BOOLEAN DEFAULT TRUE')
                ]
                
                for col_name, col_def in columns_to_add:
                    if not _column_exists(inspector, 'skill_types', col_name):
                        print(f"添加 skill_types.{col_name} 列...")
                        conn.execute(text(f"ALTER TABLE skill_types ADD COLUMN {col_name} {col_def}"))
        
        print("数据表结构更新完成")
        
    except Exception as e:
        if DB_TYPE == "mysql" and "pymysql" in str(type(e).__module__):
            print(f"MySQL数据库初始化失败: {e}")
            print("请检查：")
            print("1. MySQL服务是否已启动")
            print("2. 用户名和密码是否正确")
            print("3. MySQL是否允许本地连接")
            print("\n提示：可以设置环境变量 DB_TYPE=sqlite 使用SQLite数据库（无需MySQL服务）")
        else:
            print(f"数据库初始化失败: {e}")
        raise


def init_default_data():
    """
    初始化默认数据（课程分类、示例课程、Banner、规则内容、线下课程、技能类型等）
    """
    try:
        from app.models.course import CourseCategory, Course, SkillType
        from app.models.banner import Banner
        from app.models.rule import RuleContent
        from app.models.offline_course import OfflineCourse
        from app.database import SessionLocal
        
        db = SessionLocal()
        try:
            # 检查是否已有分类数据
            category_count = db.query(CourseCategory).count()
            skill_type_count = db.query(SkillType).count()
            
            if category_count > 0 and skill_type_count > 0:
                print("默认数据已存在，跳过初始化")
                return
            
            print("正在初始化默认数据...")
            
            # 创建技能类型（如果不存在）
            if skill_type_count == 0:
                import json
                skill_types = [
                    SkillType(
                        name="托球", skill_type="托球", icon="🤲", 
                        description="掌握正确的托球姿势和发力技巧",
                        intro="托球强调柔和却稳定的力量传递，关键在于手型扎实、脚下支撑稳固，让球在指尖形成可靠的'二传平台'。练习时要在安静状态下反复体验膝关节伸展、肩肘发力与指尖拨球三个阶段，并通过不同高度、不同节奏的抛接，让身体学会在快速跑动中依然保持手型完整。只有当托球弧线如同轨道般稳定，球队才有可能组织多变战术。",
                        focus_points=json.dumps(["手型包裹球体", "屈膝缓冲", "指尖发力"], ensure_ascii=False),
                        training_methods=json.dumps([
                            {"title": "手型练习", "desc": "在墙前反复模拟托球手型，拇指与食指呈三角支撑，感受指尖发力点。"},
                            {"title": "力量控制", "desc": "用不同高度与距离的目标练习托球，强调膝关节伸展与手臂发力的同步。"},
                            {"title": "配合训练", "desc": "与队友进行移动中的二传练习，加入临场语音沟通，培养节奏感。"}
                        ], ensure_ascii=False),
                        tips=json.dumps(["托球瞬间手腕微内扣，避免掌心触球造成持球犯规", "下肢发力先于上肢，保证力量传递顺畅", "二传前喊声清晰，便于队友判断"], ensure_ascii=False),
                        sort_order=1
                    ),
                    SkillType(
                        name="垫球", skill_type="垫球", icon="🏐", 
                        description="学习准确的垫球技术和动作要领",
                        intro="垫球是衔接防守与进攻的枢纽，讲究'下肢到手臂'一体发力与来球角度预判，确保球权延续。优秀的垫球手必须具备长期的脚步习惯：提前蹲低、脚尖点地、髋部跟随，并用眼角余光感知队友站位。训练时可以借助不同重量的球或加入旋转来增加难度，让前臂在冲击下依然保持平面。每一次成功垫球都是防守体系运转的开端。",
                        focus_points=json.dumps(["提前蹲位", "手臂锁死", "随球移动"], ensure_ascii=False),
                        training_methods=json.dumps([
                            {"title": "手臂姿势", "desc": "双前臂相贴并拢，手腕下压形成平面，两臂伸直，反复空击寻找最佳角度。"},
                            {"title": "身体协调", "desc": "用小碎步调整迎球位置，保持重心低位，体会髋部随球转动。"},
                            {"title": "接球练习", "desc": "模拟不同弧线与旋转来球，练习垫短球、垫长球的落点控制。"}
                        ], ensure_ascii=False),
                        tips=json.dumps(["迎球前保持脚尖点地便于启动", "击球瞬间用肩带动手臂，不要单纯甩腕", "学会喊'我来'减少队友抢球"], ensure_ascii=False),
                        sort_order=2
                    ),
                    SkillType(
                        name="扣球", skill_type="扣球", icon="💥", 
                        description="提升扣球力量与精准度",
                        intro="扣球结合助跑、起跳、挥臂与落地四个环节，需在最舒适的击球点释放最大动能，同时兼顾落点判断。想要扣出有威胁的球，必须在助跑阶段就设想目标窗口，并在空中通过肩部扭转寻找最佳击球角度。训练中可加入定点助跑、弹力绳抗阻以及目标靶区练习，反复强化看二传、跟球、压腕的节奏。稳定而多变的扣球，是球队终结回合的最终保证。",
                        focus_points=json.dumps(["助跑节奏", "空中拧肩", "落点观察"], ensure_ascii=False),
                        training_methods=json.dumps([
                            {"title": "起跳训练", "desc": "利用跨步 + 小跳的三步助跑提高水平速度，并通过摆臂将动量转为垂直起跳。"},
                            {"title": "击球点", "desc": "在空中保持腰腹紧绷，在手臂挥至最高点前方完成击球，确保击球点在额前上方，保证压腕动作。"},
                            {"title": "力量训练", "desc": "结合核心与上肢力量训练，使用弹力带或药球模拟挥臂，提升鞭打速度。"}
                        ], ensure_ascii=False),
                        tips=json.dumps(["起跳前盯球不过多晃头，保持视觉稳定", "扣球收腹抬膝可助力空中停留", "落地时双脚前掌缓冲，保护膝踝"], ensure_ascii=False),
                        sort_order=3
                    ),
                    SkillType(
                        name="拦网", skill_type="拦网", icon="🛡️", 
                        description="练习封锁线路、提升前排防守",
                        intro="拦网不是单纯跳起伸手，而是根据二传与攻手习惯进行路线预判，并用手掌包住球体出口形成有效封锁。高水平拦网员会在对方二传触球瞬间就启动，利用侧身小步锁定目标点，同时保持双臂贴网、腹部收紧，防止被反扑顶开。训练可分为观察练习、单人按步伐走位以及双人协同补位，让'眼到、脚到、手到'成为自然反应。一次成功的拦网，可以瞬间扭转比赛气势。",
                        focus_points=json.dumps(["观察二传", "双臂贴网", "手指盖压"], ensure_ascii=False),
                        training_methods=json.dumps([
                            {"title": "判断训练", "desc": "通过录像或实战演练分析对方二传出手高度与节奏，提前移动封锁点。"},
                            {"title": "起跳时机", "desc": "练习侧向移动到位后同时起跳，双臂贴网伸直，与队友协调形成双人拦网。"},
                            {"title": "手型控制", "desc": "双手如同'雨棚'覆盖网端，手指张开向内扣压，减少被打手出界的风险。"}
                        ], ensure_ascii=False),
                        tips=json.dumps(["拦网着地第一时间回防，避免形成空档", "与队友约定拦网手势，明确分工", "中间拦网要学会补位至边线"], ensure_ascii=False),
                        sort_order=4
                    ),
                    SkillType(
                        name="发球", skill_type="发球", icon="🎯", 
                        description="发球力量与落点双管齐下",
                        intro="发球是唯一不受对手干扰的进攻手段，要在抛球、踏步、击球三环节建立稳定节奏，再逐步加入跳发或飘球等战术变化。训练初期需反复校准抛球高度与落点，让球在肩前形成可控的击球窗口；随后通过不同击球面创造飘球、旋球或平击跳发，使对手无法轻松组织一传。结合比赛录像制定发球策略，快速识别对方一传弱点，就能把发球变成压迫性的战术武器。",
                        focus_points=json.dumps(["抛球高度一致", "击球面稳定", "落点策略"], ensure_ascii=False),
                        training_methods=json.dumps([
                            {"title": "抛球训练", "desc": "双脚不动连续抛球，确保球在额前 30cm 处达到最高点并保持垂直回落。"},
                            {"title": "挥臂击球", "desc": "用固定支点练习手臂鞭打，手掌击打球的中部或中上部，制造前旋或飘球效果。"},
                            {"title": "战术发球", "desc": "设计边线、后排与弱防守点的目标区域，结合记分板练精确落点。"}
                        ], ensure_ascii=False),
                        tips=json.dumps(["发球前先观察对方站位，选择弱点", "跳发落地时注意前后脚缓冲", "连续失误时可改用稳健飘球止损"], ensure_ascii=False),
                        sort_order=5
                    ),
                ]
                for st in skill_types:
                    db.add(st)
                db.commit()
                print("技能类型数据初始化完成")
            
            # 如果分类已存在则跳过其他初始化
            if category_count > 0:
                return
            
            # 创建课程分类
            categories = [
                CourseCategory(name="基础规则", description="排球基础规则学习", icon="📋", sort_order=1),
                CourseCategory(name="技能训练", description="排球技能提升训练", icon="⚡", sort_order=2),
                CourseCategory(name="视频课程", description="视频教学课程", icon="📹", sort_order=3),
                CourseCategory(name="反应训练", description="反应力训练", icon="🎯", sort_order=4),
            ]
            for cat in categories:
                db.add(cat)
            db.commit()
            
            # 创建示例课程
            courses = [
                Course(
                    title="托球技巧",
                    description="掌握正确的托球姿势和发力技巧",
                    skill_type="托球",
                    difficulty=2,
                    duration=15,
                    cover_image="/static/image/2.jpg",
                    sort_order=1
                ),
                Course(
                    title="垫球技巧",
                    description="学习准确的垫球技术和动作要领",
                    skill_type="垫球",
                    difficulty=2,
                    duration=20,
                    cover_image="/static/image/4.jpg",
                    sort_order=2
                ),
                Course(
                    title="扣球技巧",
                    description="提升扣球力量与精准度",
                    skill_type="扣球",
                    difficulty=4,
                    duration=25,
                    cover_image="/static/image/5.jpg",
                    sort_order=3
                ),
                Course(
                    title="拦网技巧",
                    description="掌握起跳时机与手型，打造铜墙铁壁",
                    skill_type="拦网",
                    difficulty=4,
                    duration=20,
                    cover_image="/static/image/3.jpg",
                    sort_order=4
                ),
                Course(
                    title="发球技巧",
                    description="练习力量与落点控制，发球直接得分",
                    skill_type="发球",
                    difficulty=3,
                    duration=18,
                    cover_image="/static/image/1.jpg",
                    sort_order=5
                ),
            ]
            for course in courses:
                db.add(course)
            db.commit()
            
            # 创建Banner数据
            banners = [
                Banner(
                    title="扣球瞬间",
                    image_url="/static/image/排球banner1-扣球瞬间.png",
                    link_type="page",
                    sort_order=1
                ),
                Banner(
                    title="团队比赛",
                    image_url="/static/image/排球banner2-团队比赛.png",
                    link_type="page",
                    sort_order=2
                ),
                Banner(
                    title="发球动作",
                    image_url="/static/image/排球banner3-发球动作.png",
                    link_type="page",
                    sort_order=3
                ),
            ]
            for banner in banners:
                db.add(banner)
            db.commit()
            
            # 创建规则内容
            rule_contents = [
                RuleContent(
                    title="排球基础规则",
                    content="排球是一项讲究团队协作与节奏控制的球类运动，比赛在18米×9米的场地上进行，两队各派6名队员通过最多三次触球组织进攻与防守。除了攻防转换的速度，排球还强调轮转位置、发球战术与心理博弈：每一次发球都可能成为得分起点，每一次防守成功也会反向激励队友继续拼搏。现代排球吸收了大量科学训练理念，结合体能、力量、柔韧与战术意识，让不同身高、不同特点的选手都能找到适合自己的定位；无论是初学者还是专业队员，只要掌握基本规则与安全要领，就能在这项运动里体验到协同创造价值的乐趣。",
                    section_title="基础介绍",
                    section_order=0,
                    sort_order=1
                ),
                RuleContent(
                    title="场地与人员",
                    content="排球场地为18米×9米的长方形，中间由球网分隔。每队6名队员，分为前排和后排。",
                    section_title="1. 场地与人员",
                    section_order=1,
                    image_url="https://via.placeholder.com/600x300/FFE4B5/333333?text=场地示意图",
                    sort_order=2
                ),
                RuleContent(
                    title="得分规则",
                    content="采用每球得分制，发球方得分或接发球方失误，对方得分。标准比赛采用五局三胜制，前四局先得25分且领先2分者获胜，决胜局（第五局）先得15分且领先2分者获胜。",
                    section_title="2. 得分规则",
                    section_order=2,
                    image_url="https://via.placeholder.com/600x300/FFE4B5/333333?text=得分规则",
                    sort_order=3
                ),
                RuleContent(
                    title="基本动作",
                    content="包括发球、接发球、传球、扣球、拦网和防守。每个动作都有其技术要领和规则要求。",
                    section_title="3. 基本动作",
                    section_order=3,
                    image_url="https://via.placeholder.com/600x300/FFE4B5/333333?text=基本动作",
                    sort_order=4
                ),
                RuleContent(
                    title="犯规情况",
                    content="• 持球：球在手中停留或被抛出，未形成清晰的击球动作\n• 连击：同一队员连续两次触球（拦网时除外）\n• 触网：比赛进行中，队员身体的任何部分触碰到球网\n• 过中线：队员脚完全越过中线进入对方场地\n• 四次击球：一方在将球击回对方场地前，超过三次触球",
                    section_title="4. 犯规情况",
                    section_order=4,
                    sort_order=5
                ),
            ]
            for rule in rule_contents:
                db.add(rule)
            db.commit()
            
            # 创建线下课程
            offline_courses = [
                OfflineCourse(
                    title="基础排球训练班",
                    description="适合初学者的基础训练课程，从站姿、传垫等动作逐项拆解，并配备课后家庭练习清单。",
                    location="北京市朝阳区体育馆",
                    schedule_type="weekly",
                    schedule_info="每周六 14:00-16:00",
                    price=200.0,
                    max_participants=20,
                    current_participants=12,
                    image_url="https://via.placeholder.com/400x300/FFE4B5/333333?text=基础班",
                    sort_order=1
                ),
                OfflineCourse(
                    title="进阶技能提升班",
                    description="针对有一定基础的学员，重点拆解扣球、拦网等进攻套路，附带专项体能课与战术对抗。",
                    location="上海市浦东新区体育中心",
                    schedule_type="weekly",
                    schedule_info="每周日 10:00-12:00",
                    price=300.0,
                    max_participants=15,
                    current_participants=8,
                    image_url="https://via.placeholder.com/400x300/FFE4B5/333333?text=进阶班",
                    sort_order=2
                ),
                OfflineCourse(
                    title="青少年排球训练营",
                    description="专为青少年设计的训练课程，融合兴趣小游戏、身体协调与基础技术打磨，帮助孩子从玩耍走向系统训练。",
                    location="广州市天河区运动场",
                    schedule_type="weekly",
                    schedule_info="每周三、五 16:00-18:00",
                    price=150.0,
                    max_participants=30,
                    current_participants=25,
                    image_url="https://via.placeholder.com/400x300/FFE4B5/333333?text=青少年",
                    sort_order=3
                ),
                OfflineCourse(
                    title="专业教练一对一",
                    description="专业教练一对一指导，可根据比赛录像制定矫正方案，迅速提升个人短板。",
                    location="深圳市南山区体育馆",
                    schedule_type="appointment",
                    schedule_info="预约制",
                    price=500.0,
                    max_participants=1,
                    current_participants=1,
                    image_url="https://via.placeholder.com/400x300/FFE4B5/333333?text=一对一",
                    sort_order=4
                ),
            ]
            for course in offline_courses:
                db.add(course)
            db.commit()
            
            print("默认数据初始化完成")
        finally:
            db.close()
    except Exception as e:
        print(f"初始化默认数据失败: {e}")
        # 不抛出异常，避免影响应用启动

