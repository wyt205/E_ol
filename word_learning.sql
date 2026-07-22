/*
 Navicat Premium Data Transfer

 Source Server         : test
 Source Server Type    : MySQL
 Source Server Version : 80300 (8.3.0)
 Source Host           : localhost:3306
 Source Schema         : word_learning

 Target Server Type    : MySQL
 Target Server Version : 80300 (8.3.0)
 File Encoding         : 65001

 Date: 21/07/2026 01:28:30
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for favorites
-- ----------------------------
DROP TABLE IF EXISTS `favorites`;
CREATE TABLE `favorites`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '收藏ID',
  `user_id` int NOT NULL COMMENT '用户ID',
  `word_id` int NOT NULL COMMENT '单词ID',
  `created_at` datetime NULL DEFAULT (now()) COMMENT '收藏时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `unique_user_word_favorite`(`user_id` ASC, `word_id` ASC) USING BTREE,
  INDEX `word_id`(`word_id` ASC) USING BTREE,
  INDEX `ix_favorites_id`(`id` ASC) USING BTREE,
  CONSTRAINT `favorites_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `favorites_ibfk_2` FOREIGN KEY (`word_id`) REFERENCES `words` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 23 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of favorites
-- ----------------------------
INSERT INTO `favorites` VALUES (22, 5, 1, '2026-07-21 00:49:32');

-- ----------------------------
-- Table structure for mistakes
-- ----------------------------
DROP TABLE IF EXISTS `mistakes`;
CREATE TABLE `mistakes`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '错题ID',
  `user_id` int NOT NULL COMMENT '用户ID',
  `word_id` int NOT NULL COMMENT '单词ID',
  `mistake_count` int NOT NULL COMMENT '错误次数',
  `created_at` datetime NULL DEFAULT (now()) COMMENT '首次错误时间',
  `updated_at` datetime NULL DEFAULT (now()) COMMENT '最后错误时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `unique_user_word_mistake`(`user_id` ASC, `word_id` ASC) USING BTREE,
  INDEX `word_id`(`word_id` ASC) USING BTREE,
  INDEX `ix_mistakes_id`(`id` ASC) USING BTREE,
  CONSTRAINT `mistakes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `mistakes_ibfk_2` FOREIGN KEY (`word_id`) REFERENCES `words` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 11 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of mistakes
-- ----------------------------
INSERT INTO `mistakes` VALUES (10, 5, 1, 1, '2026-07-21 00:06:49', '2026-07-21 00:06:49');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '登录用户名',
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '登录密码',
  `nickname` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '' COMMENT '用户昵称',
  `role` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'user' COMMENT '角色：admin=管理员, user=普通用户',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active' COMMENT '状态：active=启用, disabled=禁用',
  `avatar` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '' COMMENT '头像URL（预留）',
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '' COMMENT '邮箱（预留）',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '用户表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, 'admin', '123456', '系统管理员', 'admin', 'active', '', 'admin', '2026-07-07 15:05:22', '2026-07-07 15:59:14');
INSERT INTO `users` VALUES (2, 'zhangsan', '123456', '张三', 'user', 'active', '', 'zhangsan@qq.com', '2026-07-07 15:05:22', '2026-07-07 15:47:29');
INSERT INTO `users` VALUES (3, 'lisi', '123456', '李四', 'user', 'active', '', 'lisi@qq.com', '2026-07-07 15:05:22', '2026-07-07 15:47:38');
INSERT INTO `users` VALUES (4, 'wangwu', '123456', '王五', 'user', 'disabled', '', 'wangwu@qq.com', '2026-07-07 15:05:22', '2026-07-07 15:47:49');
INSERT INTO `users` VALUES (5, 'user_1783411312', '123456', 'wyt', 'user', 'active', '', 'wyt@qq.com', '2026-07-07 16:01:52', '2026-07-07 17:00:45');

-- ----------------------------
-- Table structure for word_lists
-- ----------------------------
DROP TABLE IF EXISTS `word_lists`;
CREATE TABLE `word_lists`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '词表ID',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '词表名称',
  `description` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '词表描述',
  `created_at` datetime NULL DEFAULT (now()) COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name` ASC) USING BTREE,
  INDEX `ix_word_lists_id`(`id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of word_lists
-- ----------------------------
INSERT INTO `word_lists` VALUES (1, '默认词表', '系统默认单词表', '2026-07-05 01:03:21');

-- ----------------------------
-- Table structure for words
-- ----------------------------
DROP TABLE IF EXISTS `words`;
CREATE TABLE `words`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '单词ID',
  `list_id` int NOT NULL DEFAULT 1 COMMENT '词表ID',
  `word` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '单词',
  `phonetic_uk` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT 'UK音标',
  `phonetic_us` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT 'US音标',
  `audio_url_uk` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT 'UK语音URL',
  `audio_url_us` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT 'US语音URL',
  `meaning` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '释义',
  `example` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '例句',
  `example_translation` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '例句翻译',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `list_id`(`list_id` ASC) USING BTREE,
  CONSTRAINT `words_ibfk_1` FOREIGN KEY (`list_id`) REFERENCES `word_lists` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '单词表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of words
-- ----------------------------
INSERT INTO `words` VALUES (1, 1, 'atest', '/ˈtest/', '/ˈtest/', NULL, NULL, '测试单词11', 'This is a test.11', '这是一个测试。', '2026-07-20 19:54:00');
INSERT INTO `words` VALUES (2, 1, 'example', '/ɪɡˈzɑːmpl/', '/ɪɡˈzæmpl/', NULL, NULL, '例子', 'This is an example.', '这是一个例子。', '2026-07-20 19:54:00');
INSERT INTO `words` VALUES (3, 1, 'word', '/wɜːrd/', '/wɜːrd/', NULL, NULL, '单词', 'A word is a unit of language.', '单词是语言的单位。', '2026-07-20 19:54:00');

SET FOREIGN_KEY_CHECKS = 1;
