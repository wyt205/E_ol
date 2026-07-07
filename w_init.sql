CREATE DATABASE IF NOT EXISTS word_learning DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE word_learning;

-- ===== 用户表 =====
-- 存储所有用户账号（管理员 + 普通用户）
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '登录用户名',
    password VARCHAR(255) NOT NULL COMMENT '登录密码',
    nickname VARCHAR(100) DEFAULT '' COMMENT '用户昵称',
    role VARCHAR(20) NOT NULL DEFAULT 'user' COMMENT '角色：admin=管理员, user=普通用户',
    status VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '状态：active=启用, disabled=禁用',
    avatar VARCHAR(500) DEFAULT '' COMMENT '头像URL（预留）',
    email VARCHAR(100) DEFAULT '' COMMENT '邮箱（预留）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 插入默认管理员账号（密码：123456）
INSERT INTO users (username, password, nickname, role, status, email) VALUES
('admin', '123456', '系统管理员', 'admin', 'active', 'admin@wordlearning.com');

-- 插入几个测试普通用户
INSERT INTO users (username, password, nickname, role, status, email) VALUES
('zhangsan', '123456', '张三', 'user', 'active', 'zhangsan@example.com'),
('lisi', '123456', '李四', 'user', 'active', 'lisi@example.com'),
('wangwu', '123456', '王五', 'user', 'disabled', 'wangwu@example.com');

-- ===== 单词表（词表分类） =====
CREATE TABLE IF NOT EXISTS word_lists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(500) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入默认词表
INSERT INTO word_lists (name, description) VALUES ('默认词表', '系统默认单词表');

-- ===== 单词表 =====
CREATE TABLE IF NOT EXISTS words (
    id INT AUTO_INCREMENT PRIMARY KEY,
    list_id INT NOT NULL DEFAULT 1,
    word VARCHAR(100) NOT NULL,
    phonetic VARCHAR(100),
    meaning TEXT NOT NULL,
    example TEXT,
    example_translation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (list_id) REFERENCES word_lists(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO words (list_id, word, phonetic, meaning, example, example_translation) VALUES
(1, 'apple', '/ˈæpl/', '苹果', 'I eat an apple every day.', '我每天吃一个苹果。'),
(1, 'banana', '/bəˈnænə/', '香蕉', 'Bananas are rich in potassium.', '香蕉富含钾。'),
(1, 'computer', '/kəmˈpjuːtər/', '电脑', 'I use my computer for work.', '我用电脑工作。'),
(1, 'development', '/dɪˈveləpmənt/', '发展；开发', 'Software development is my job.', '软件开发是我的工作。'),
(1, 'education', '/ˌedʒuˈkeɪʃn/', '教育', 'Education is very important.', '教育非常重要。'),
(1, 'friend', '/frend/', '朋友', 'She is my best friend.', '她是我最好的朋友。'),
(1, 'guitar', '/ɡɪˈtɑːr/', '吉他', 'He plays the guitar very well.', '他吉他弹得非常好。'),
(1, 'happiness', '/ˈhæpinəs/', '幸福；快乐', 'Money cannot buy happiness.', '金钱买不到幸福。'),
(1, 'important', '/ɪmˈpɔːrtnt/', '重要的', 'This meeting is very important.', '这次会议非常重要。'),
(1, 'journey', '/ˈdʒɜːrni/', '旅程', 'Life is a long journey.', '人生是一段漫长的旅程。');