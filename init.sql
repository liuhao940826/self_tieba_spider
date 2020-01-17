-- 只要用户的详情页链接另外一个爬虫读取了去统计
-- CREATE TABLE `user_outer_Info` (
--   `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键',
--   `channel_type` tinyint(4) DEFAULT NULL COMMENT '1:微博 2:贴吧 3:直播 4:qq 5:微信',
--   `user_name` varchar(48) DEFAULT NULL,
--   `tieba_age` varchar(48) DEFAULT NULL,
--   `post_num` int(11) DEFAULT NULL,
--   `active_tieba` varchar(255) DEFAULT NULL,
--   PRIMARY KEY (`id`)
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `comment` (
  `id` bigint(12) NOT NULL,
  `author_id` varchar(48) DEFAULT NULL,
  `author` varchar(30) DEFAULT NULL,
  `content` text,
  `time` datetime DEFAULT NULL,
  `post_id` bigint(12) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `post` (
  `id` bigint(12) NOT NULL,
  `floor` int(4) DEFAULT NULL,
  `user_detail_href` varchar(255) DEFAULT NULL,
  `author_id` varchar(48) DEFAULT NULL,
  `author` varchar(30) DEFAULT NULL,
  `content` text,
  `time` datetime DEFAULT NULL,
  `comment_num` int(4) DEFAULT NULL,
  `thread_id` bigint(12) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `thread` (
  `id` bigint(12) NOT NULL,
  `tb_name` varchar(100) DEFAULT NULL,
  `title` varchar(100) DEFAULT NULL,
  `author_id` varchar(48) DEFAULT NULL,
  `author` varchar(30) DEFAULT NULL,
  `reply_num` int(4) DEFAULT NULL,
  `good` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;









