SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for historical_train
-- ----------------------------
DROP TABLE IF EXISTS `historical_train`;
CREATE TABLE `historical_train` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_coin` smallint(6) DEFAULT NULL,
  `time_create` int(11) DEFAULT NULL,
  `price_test` text,
  `price_predict` text,
  `RMSE` float DEFAULT NULL,
  `max_error` float DEFAULT NULL,
  `openTime_last` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `time_create` (`time_create`)
) ENGINE=InnoDB AUTO_INCREMENT=296 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for historical_price_predictions
-- ----------------------------
DROP TABLE IF EXISTS `historical_price_predictions`;
CREATE TABLE `historical_price_predictions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_coin` smallint(6) DEFAULT NULL,
  `time_create` int(11) DEFAULT NULL,
  `price_predict` text,
  `price_actual` text,
  `price_preidct_last` float DEFAULT NULL,
  `price_predict_previous` float DEFAULT NULL,
  `price_actual_last` float DEFAULT NULL,
  `price_actual_previous` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `time_create` (`time_create`)
) ENGINE=InnoDB AUTO_INCREMENT=5153 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for coin_info
-- ----------------------------
DROP TABLE IF EXISTS `coin_info`;
CREATE TABLE `coin_info` (
  `id` smallint(6) NOT NULL AUTO_INCREMENT,
  `symbol` char(20) DEFAULT NULL,
  `minQty` decimal(15,10) DEFAULT NULL,
  `tickSize` decimal(15,10) DEFAULT NULL,
  `status` char(20) DEFAULT NULL,
  `baseAsset` char(10) DEFAULT NULL,
  `quoteAsset` char(10) DEFAULT NULL,
  `openTime_last` bigint(20) DEFAULT NULL,
  `max_error` float DEFAULT NULL,
  `RMSE` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `symbol` (`symbol`) USING HASH
) ENGINE=InnoDB AUTO_INCREMENT=399 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for candlestick_data
-- ----------------------------
DROP TABLE IF EXISTS `candlestick_data`;
CREATE TABLE `candlestick_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idCoin` smallint(6) DEFAULT NULL,
  `openTime` bigint(20) DEFAULT NULL,
  `open` decimal(20,10) DEFAULT NULL,
  `high` decimal(20,10) DEFAULT NULL,
  `low` decimal(20,10) DEFAULT NULL,
  `close` decimal(20,10) DEFAULT NULL,
  `volume` decimal(20,10) DEFAULT NULL,
  `closeTime` bigint(20) DEFAULT NULL,
  `quoteAssetVolume` decimal(20,10) DEFAULT NULL,
  `numberOfTrader` int(11) DEFAULT NULL,
  `takerBuyBaseAssetVolume` decimal(20,10) DEFAULT NULL,
  `takerBuyQuoteAssetVolume` decimal(20,10) DEFAULT NULL,
  `ignore` decimal(20,10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `openTime` (`openTime`),
  KEY `idCoin` (`idCoin`)
) ENGINE=InnoDB AUTO_INCREMENT=2769604 DEFAULT CHARSET=utf8;
