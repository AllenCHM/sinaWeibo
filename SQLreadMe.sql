CREATE TABLE `weibo` (
  `uid` varchar(20) NOT NULL COMMENT '用户id',
  `sex` varchar(10) DEFAULT NULL COMMENT '性别',
  `place` varchar(50) DEFAULT NULL COMMENT '现居地',
  `school` varchar(255) DEFAULT NULL COMMENT '院校',
  `profile` varchar(255) DEFAULT NULL COMMENT '个人简介',
  `weiboText` varchar(255) DEFAULT NULL COMMENT '微博文本内容',
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
