-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: educational_platform_db
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `tbl_answer`
--

DROP TABLE IF EXISTS `tbl_answer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_answer` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `QuestionID` int DEFAULT NULL,
  `AnswerName` varchar(1000) DEFAULT NULL,
  `AnswerType` varchar(255) DEFAULT NULL,
  `DescriptionID` int DEFAULT NULL,
  `SequenceNo` int DEFAULT NULL,
  `Active` bit(1) DEFAULT b'1',
  `CreatedOn` datetime DEFAULT CURRENT_TIMESTAMP,
  `CreatedBy` varchar(255) DEFAULT NULL,
  `LastUpdatedOn` datetime DEFAULT NULL,
  `LastUpdatedBy` varchar(255) DEFAULT NULL,
  `IsCorrect` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ID`),
  KEY `QuestionID` (`QuestionID`),
  KEY `DescriptionID` (`DescriptionID`),
  CONSTRAINT `tbl_answer_ibfk_1` FOREIGN KEY (`QuestionID`) REFERENCES `tbl_question` (`ID`),
  CONSTRAINT `tbl_answer_ibfk_2` FOREIGN KEY (`DescriptionID`) REFERENCES `tbl_description` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_answer`
--

LOCK TABLES `tbl_answer` WRITE;
/*!40000 ALTER TABLE `tbl_answer` DISABLE KEYS */;
INSERT INTO `tbl_answer` VALUES (1,1,'1 time',NULL,NULL,NULL,_binary '','2025-07-28 14:51:26','Admin',NULL,NULL,0),(2,1,'10 times',NULL,NULL,NULL,_binary '','2025-07-28 14:51:26','Admin',NULL,NULL,1),(3,1,'100 times',NULL,NULL,NULL,_binary '','2025-07-28 14:51:26','Admin',NULL,NULL,0),(4,1,'20 times',NULL,NULL,NULL,_binary '','2025-07-28 14:51:26','Admin',NULL,NULL,0),(13,2,'1 time',NULL,NULL,NULL,_binary '','2025-07-28 18:40:47','Admin',NULL,NULL,0),(14,2,'20 times',NULL,NULL,NULL,_binary '','2025-07-28 18:40:47','Admin',NULL,NULL,0),(15,2,'10 times',NULL,NULL,NULL,_binary '','2025-07-28 18:40:47','Admin',NULL,NULL,1),(16,2,'100 times',NULL,NULL,NULL,_binary '','2025-07-28 18:40:47','Admin',NULL,NULL,0);
/*!40000 ALTER TABLE `tbl_answer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_description`
--

DROP TABLE IF EXISTS `tbl_description`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_description` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `LanguageID` int DEFAULT NULL,
  `DescriptionText` text,
  `DescriptionImage` blob,
  `DescriptionURL` varchar(2048) DEFAULT NULL,
  `DescriptionType` varchar(255) DEFAULT NULL,
  `Active` bit(1) DEFAULT b'1',
  `CreatedOn` datetime DEFAULT CURRENT_TIMESTAMP,
  `CreatedBy` varchar(255) DEFAULT NULL,
  `LastUpdatedOn` datetime DEFAULT NULL,
  `LastUpdatedBy` varchar(255) DEFAULT NULL,
  `SectionName` varchar(255) DEFAULT NULL,
  `TopicID` int DEFAULT NULL,
  `DescriptionOrder` int NOT NULL,
  `InteractiveElementID` int DEFAULT NULL,
  `ContentType` varchar(50) NOT NULL DEFAULT 'Paragraph',
  PRIMARY KEY (`ID`),
  KEY `fk_description_topic` (`TopicID`),
  KEY `fk_Description_InteractiveElement` (`InteractiveElementID`),
  CONSTRAINT `fk_Description_InteractiveElement` FOREIGN KEY (`InteractiveElementID`) REFERENCES `tbl_interactiveelement` (`ID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_description_topic` FOREIGN KEY (`TopicID`) REFERENCES `tbl_topic` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_description`
--

LOCK TABLES `tbl_description` WRITE;
/*!40000 ALTER TABLE `tbl_description` DISABLE KEYS */;
INSERT INTO `tbl_description` VALUES (1,NULL,'Detective Mila stepped into the dusty hall of clocks. Every clock was missing its hour handΓÇöbut that wasnΓÇÖt the weird part. On one wall, someone had taped a note: ΓÇ£I moved one digit. Now your treasure is worth less.ΓÇ¥ Mila gasped. Her eyes darted to the glowing vault screen. The number: 7,452.',NULL,NULL,NULL,_binary '','2025-07-28 17:49:06','Admin',NULL,NULL,'Hook',2,1,NULL,'Paragraph'),(2,NULL,'Mila must figure out how the thief changed the number using digit value. She will build a bar model to trace each digitΓÇÖs place and compare old vs. new. This is the only way to see what was lost.',NULL,NULL,NULL,_binary '','2025-07-28 17:49:06','Admin',NULL,NULL,'BRIDGE',2,2,NULL,'Paragraph'),(3,NULL,'Intent: \"IΓÇÖll map this number outΓÇödigit by digit.\"\nTool: \"LetΓÇÖs draw a bar model. One bar for each digit, left to right.\"\nReason: \"That shows how much each digit is really worth.\"\n\nMila laid out four bars:\n\n\"Left bar: mark 7, thatΓÇÖs the thousandsΓÇö7,000.\"\n\n\"Next is 4ΓÇöhundreds. ThatΓÇÖs 400.\"\n\n\"Next is 5ΓÇötens. ThatΓÇÖs 50.\"\n\n\"Last is 2ΓÇöones. ThatΓÇÖs just 2.\"\n\nMila stared at the screen. ΓÇ£So the value was 7,452. Now to figure out what changed.ΓÇ¥',NULL,NULL,NULL,_binary '','2025-07-28 17:49:06','Admin',NULL,NULL,'Scene 1',2,3,NULL,'Paragraph'),(4,NULL,'Intent: \"LetΓÇÖs test if a digit was moved.\"\nTool: \"IΓÇÖll move the 5 from the tens bar to the thousands bar.\"\nReason: \"ThatΓÇÖs the biggest jump. LetΓÇÖs see the new value.\"\n\nMila redrew the bars:\n\n\"Thousands: 5 now, so 5,000.\"\n\n\"Hundreds: still 4, or 400.\"\n\n\"Tens: now has 7, or 70.\"\n\n\"Ones: still 2.\"\n\nShe added: \"New number is 5,472. But waitΓÇª thatΓÇÖs higher, not lower!\"\n\nMistake spotted.\n\n',NULL,NULL,NULL,_binary '','2025-07-28 17:49:06','Admin',NULL,NULL,'Scene 2',2,4,NULL,'Paragraph'),(5,NULL,'Intent: \"Okay, letΓÇÖs try again. What if the 7 was moved down?\"\nTool: \"Bar model again. Move the 7 from thousands to tens.\"\nReason: \"That should shrink it.\"\n\nMila redrew:\n\n\"Thousands: now 4, or 4,000.\"\n\n\"Hundreds: still 5, or 500.\"\n\n\"Tens: now 7, or 70.\"\n\n\"Ones: still 2.\"\n\nMila said: \"New number is 4,572. LetΓÇÖs check difference: 7,452 - 4,572 = 2,880. ThatΓÇÖs a big loss!\"\n\nSuccess. \"Now I seeΓÇömoving the 7 down dropped the whole value.\"',NULL,NULL,NULL,_binary '','2025-07-28 17:49:06','Admin',NULL,NULL,'Scene 3',2,5,NULL,'Paragraph'),(6,NULL,'Intent: \"LetΓÇÖs compare side-by-side.\"\nTool: \"Build a second bar model to match the changed number.\"\nReason: \"I need to show where each digitΓÇÖs value shifted.\"\n\nMila pointed:\n\n\"Old thousands bar: 7,000 ΓåÆ New: 4,000.\"\n\n\"Old tens bar: 50 ΓåÆ New: 70.\"\n\n\"So the 7 moved from 7,000 to 70. ThatΓÇÖs the trick!\"\n\nShe circled the bars. \"The thief didnΓÇÖt change digitsΓÇöjust the place.\"',NULL,NULL,NULL,_binary '','2025-07-28 17:49:06','Admin',NULL,NULL,'Scene 4',2,6,NULL,'Paragraph'),(7,NULL,'Intent: \"Now IΓÇÖll prove the thief used the same digits.\"\nTool: \"Use both bar models and compare totals.\"\nReason: \"That will show the digits are the same, but place changed.\"\n\nMila stacked both bars:\n\n\"First: 7,000 + 400 + 50 + 2 = 7,452.\"\n\n\"Second: 4,000 + 500 + 70 + 2 = 4,572.\"\n\n\"Same digits. Different places. Same pieces. New total. ThatΓÇÖs how place changes value.\"\n\nThe vault clicked open.',NULL,NULL,NULL,_binary '','2025-07-28 17:49:06','Admin',NULL,NULL,'Scene 5',2,7,NULL,'Paragraph'),(8,NULL,'To catch the number switch, Mila used bar models twice. Each bar showed how digit place affects total. One mistake was moving 5 up to thousandsΓÇöit looked right, but made the number too big. She fixed it by trying a lower move. The key is to trace each digitΓÇÖs place value. If stuck, rebuild the bar.',NULL,NULL,NULL,_binary '','2025-07-28 17:49:06','Admin',NULL,NULL,'Summary',2,8,NULL,'Paragraph');
/*!40000 ALTER TABLE `tbl_description` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_flagreport`
--

DROP TABLE IF EXISTS `tbl_flagreport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_flagreport` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `UserID` int NOT NULL,
  `FlaggedItemID` int NOT NULL,
  `ItemType` enum('Question','Story') NOT NULL,
  `Reason` text,
  `Status` enum('Pending','Reviewed','Dismissed') DEFAULT 'Pending',
  `ReportedOn` datetime DEFAULT CURRENT_TIMESTAMP,
  `ResolvedOn` datetime DEFAULT NULL,
  `ResolvedBy` int DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `UserID` (`UserID`),
  KEY `ResolvedBy` (`ResolvedBy`),
  CONSTRAINT `tbl_flagreport_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `tbl_user` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `tbl_flagreport_ibfk_2` FOREIGN KEY (`ResolvedBy`) REFERENCES `tbl_user` (`ID`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_flagreport`
--

LOCK TABLES `tbl_flagreport` WRITE;
/*!40000 ALTER TABLE `tbl_flagreport` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_flagreport` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_grade`
--

DROP TABLE IF EXISTS `tbl_grade`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_grade` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `GradeName` varchar(255) NOT NULL,
  `DescriptionID` int DEFAULT NULL,
  `Active` bit(1) DEFAULT b'1',
  `CreatedOn` datetime DEFAULT CURRENT_TIMESTAMP,
  `CreatedBy` varchar(255) DEFAULT NULL,
  `LastUpdatedOn` datetime DEFAULT NULL,
  `LastUpdatedBy` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `DescriptionID` (`DescriptionID`),
  CONSTRAINT `tbl_grade_ibfk_1` FOREIGN KEY (`DescriptionID`) REFERENCES `tbl_description` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_grade`
--

LOCK TABLES `tbl_grade` WRITE;
/*!40000 ALTER TABLE `tbl_grade` DISABLE KEYS */;
INSERT INTO `tbl_grade` VALUES (1,'4th Grade',NULL,_binary '','2025-07-28 14:46:22','ManualInsert',NULL,NULL),(2,'4th Grade',NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(3,'5th Grade',NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(4,'6th Grade',NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(5,'7th Grade',NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(6,'8th Grade',NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(7,'Algebra I',NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(8,'Geometry',NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL);
/*!40000 ALTER TABLE `tbl_grade` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_interactiveelement`
--

DROP TABLE IF EXISTS `tbl_interactiveelement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_interactiveelement` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `ElementType` varchar(50) NOT NULL COMMENT 'e.g., FractionBuilder, EquationBalancer, ShapeManipulator',
  `Configuration` json NOT NULL COMMENT 'JSON object storing specific settings for the element',
  `CreatedOn` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `CreatedBy` varchar(50) DEFAULT 'SYSTEM',
  `LastUpdatedOn` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `LastUpdatedBy` varchar(50) DEFAULT 'SYSTEM',
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_interactiveelement`
--

LOCK TABLES `tbl_interactiveelement` WRITE;
/*!40000 ALTER TABLE `tbl_interactiveelement` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_interactiveelement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_question`
--

DROP TABLE IF EXISTS `tbl_question`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_question` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `TopicID` int DEFAULT NULL,
  `QuestionName` varchar(1000) DEFAULT NULL,
  `QuestionType` varchar(255) NOT NULL,
  `DescriptionID` int DEFAULT NULL,
  `SequenceNo` int DEFAULT NULL,
  `Active` bit(1) DEFAULT b'1',
  `CreatedOn` datetime DEFAULT CURRENT_TIMESTAMP,
  `CreatedBy` varchar(255) DEFAULT NULL,
  `LastUpdatedOn` datetime DEFAULT NULL,
  `LastUpdatedBy` varchar(255) DEFAULT NULL,
  `DifficultyRating` int DEFAULT '3',
  PRIMARY KEY (`ID`),
  KEY `TopicID` (`TopicID`),
  KEY `DescriptionID` (`DescriptionID`),
  CONSTRAINT `tbl_question_ibfk_1` FOREIGN KEY (`TopicID`) REFERENCES `tbl_topic` (`ID`),
  CONSTRAINT `tbl_question_ibfk_2` FOREIGN KEY (`DescriptionID`) REFERENCES `tbl_description` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_question`
--

LOCK TABLES `tbl_question` WRITE;
/*!40000 ALTER TABLE `tbl_question` DISABLE KEYS */;
INSERT INTO `tbl_question` VALUES (1,2,' Look at the number 22. How many times larger is the value of the 2 in the tens place compared to the 2 in the ones place?','MultipleChoice',NULL,NULL,_binary '','2025-07-28 14:51:26','Admin',NULL,NULL,1),(2,2,'In the number 55, the 5 in the tens place is how many times larger than the 5 in the ones place?','MultipleChoice',NULL,NULL,_binary '','2025-07-28 14:56:58','Admin','2025-07-28 18:40:47','Admin',1);
/*!40000 ALTER TABLE `tbl_question` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_questionattempt`
--

DROP TABLE IF EXISTS `tbl_questionattempt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_questionattempt` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `UserID` int NOT NULL,
  `QuestionID` int NOT NULL,
  `AttemptTime` datetime DEFAULT CURRENT_TIMESTAMP,
  `UserAnswer` text,
  `IsCorrect` tinyint(1) NOT NULL,
  `DifficultyAtAttempt` int DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `UserID` (`UserID`),
  KEY `QuestionID` (`QuestionID`),
  CONSTRAINT `tbl_questionattempt_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `tbl_user` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `tbl_questionattempt_ibfk_2` FOREIGN KEY (`QuestionID`) REFERENCES `tbl_question` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_questionattempt`
--

LOCK TABLES `tbl_questionattempt` WRITE;
/*!40000 ALTER TABLE `tbl_questionattempt` DISABLE KEYS */;
INSERT INTO `tbl_questionattempt` VALUES (1,9,1,'2025-07-28 17:52:03','10 times',0,1);
/*!40000 ALTER TABLE `tbl_questionattempt` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_questiongrade`
--

DROP TABLE IF EXISTS `tbl_questiongrade`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_questiongrade` (
  `QuestionID` int NOT NULL,
  `GradeID` int NOT NULL,
  `QuestionSeverity` int DEFAULT NULL,
  `Active` bit(1) DEFAULT b'1',
  `CreatedOn` datetime DEFAULT CURRENT_TIMESTAMP,
  `CreatedBy` varchar(255) DEFAULT NULL,
  `LastUpdatedOn` datetime DEFAULT NULL,
  `LastUpdatedBy` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`QuestionID`,`GradeID`),
  KEY `GradeID` (`GradeID`),
  CONSTRAINT `tbl_questiongrade_ibfk_1` FOREIGN KEY (`QuestionID`) REFERENCES `tbl_question` (`ID`),
  CONSTRAINT `tbl_questiongrade_ibfk_2` FOREIGN KEY (`GradeID`) REFERENCES `tbl_grade` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_questiongrade`
--

LOCK TABLES `tbl_questiongrade` WRITE;
/*!40000 ALTER TABLE `tbl_questiongrade` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_questiongrade` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_step`
--

DROP TABLE IF EXISTS `tbl_step`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_step` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `QuestionID` int DEFAULT NULL,
  `StepName` varchar(1000) DEFAULT NULL,
  `StepType` int DEFAULT NULL,
  `DescriptionID` int DEFAULT NULL,
  `SequenceNo` int DEFAULT NULL,
  `Active` bit(1) DEFAULT b'1',
  `CreatedOn` datetime DEFAULT CURRENT_TIMESTAMP,
  `CreatedBy` varchar(255) DEFAULT NULL,
  `LastUpdatedOn` datetime DEFAULT NULL,
  `LastUpdatedBy` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `QuestionID` (`QuestionID`),
  KEY `DescriptionID` (`DescriptionID`),
  CONSTRAINT `tbl_step_ibfk_1` FOREIGN KEY (`QuestionID`) REFERENCES `tbl_question` (`ID`),
  CONSTRAINT `tbl_step_ibfk_2` FOREIGN KEY (`DescriptionID`) REFERENCES `tbl_description` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_step`
--

LOCK TABLES `tbl_step` WRITE;
/*!40000 ALTER TABLE `tbl_step` DISABLE KEYS */;
INSERT INTO `tbl_step` VALUES (1,1,'The Goal: We need to compare the value of the two digits in the number 22.',NULL,NULL,1,_binary '','2025-07-28 14:51:26','Admin',NULL,NULL),(2,1,'The Analogy (Money): Think of the ones place as pennies and the tens place as dimes.',NULL,NULL,2,_binary '','2025-07-28 14:51:26','Admin',NULL,NULL),(3,1,'The \'2\' in the ones place is like 2 pennies (2 cents).',NULL,NULL,3,_binary '','2025-07-28 14:51:26','Admin',NULL,NULL),(4,1,'The \'2\' in the tens place is like 2 dimes (20 cents).',NULL,NULL,4,_binary '','2025-07-28 14:51:26','Admin',NULL,NULL),(5,1,'The Comparison: How many times bigger is 20 cents than 2 cents? It\'s 10 times bigger.',NULL,NULL,5,_binary '','2025-07-28 14:51:26','Admin',NULL,NULL),(6,1,'The Rule: Every time a digit moves one spot to the left on the place value chart, its value becomes 10 times larger.',NULL,NULL,6,_binary '','2025-07-28 14:51:26','Admin',NULL,NULL),(19,2,'The Goal: We need to compare the value of the two digits in the number 22.',NULL,NULL,1,_binary '','2025-07-28 18:40:47','Admin',NULL,NULL),(20,2,'The Analogy (Money): Think of the ones place as pennies and the tens place as dimes.',NULL,NULL,2,_binary '','2025-07-28 18:40:47','Admin',NULL,NULL),(21,2,'The \'5\' in the ones place is like 5 pennies (5 cents)',NULL,NULL,3,_binary '','2025-07-28 18:40:47','Admin',NULL,NULL),(22,2,'The \'5\' in the tens place is like 5 dimes (50 cents).',NULL,NULL,4,_binary '','2025-07-28 18:40:47','Admin',NULL,NULL),(23,2,'The Comparison: How many times bigger is 50 cents than 5 cents? It\'s 10 times bigger.',NULL,NULL,5,_binary '','2025-07-28 18:40:47','Admin',NULL,NULL),(24,2,'The Rule: Every time a digit moves one spot to the left on the place value chart, its value becomes 10 times larger.',NULL,NULL,6,_binary '','2025-07-28 18:40:47','Admin',NULL,NULL);
/*!40000 ALTER TABLE `tbl_step` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_storycontentblock`
--

DROP TABLE IF EXISTS `tbl_storycontentblock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_storycontentblock` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `StorySectionID` int NOT NULL,
  `ContentType` enum('Paragraph','Interactive') NOT NULL,
  `ContentText` text,
  `InteractiveElementID` int DEFAULT NULL,
  `BlockOrder` int NOT NULL,
  `CreatedOn` datetime DEFAULT CURRENT_TIMESTAMP,
  `CreatedBy` varchar(255) DEFAULT NULL,
  `LastUpdatedOn` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `LastUpdatedBy` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `StorySectionID` (`StorySectionID`,`BlockOrder`),
  KEY `InteractiveElementID` (`InteractiveElementID`),
  CONSTRAINT `tbl_storycontentblock_ibfk_1` FOREIGN KEY (`StorySectionID`) REFERENCES `tbl_storysection` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `tbl_storycontentblock_ibfk_2` FOREIGN KEY (`InteractiveElementID`) REFERENCES `tbl_interactiveelement` (`ID`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_storycontentblock`
--

LOCK TABLES `tbl_storycontentblock` WRITE;
/*!40000 ALTER TABLE `tbl_storycontentblock` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_storycontentblock` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_storysection`
--

DROP TABLE IF EXISTS `tbl_storysection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_storysection` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `TopicID` int NOT NULL,
  `SectionName` varchar(255) NOT NULL,
  `SectionOrder` int NOT NULL,
  `CreatedOn` datetime DEFAULT CURRENT_TIMESTAMP,
  `CreatedBy` varchar(255) DEFAULT NULL,
  `LastUpdatedOn` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `LastUpdatedBy` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `TopicID` (`TopicID`,`SectionOrder`),
  CONSTRAINT `tbl_storysection_ibfk_1` FOREIGN KEY (`TopicID`) REFERENCES `tbl_topic` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_storysection`
--

LOCK TABLES `tbl_storysection` WRITE;
/*!40000 ALTER TABLE `tbl_storysection` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_storysection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_subject`
--

DROP TABLE IF EXISTS `tbl_subject`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_subject` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `SubjectName` varchar(255) NOT NULL,
  `SubjectType` varchar(255) DEFAULT NULL,
  `DescriptionID` int DEFAULT NULL,
  `SequenceNo` int DEFAULT NULL,
  `Active` bit(1) DEFAULT b'1',
  `CreatedOn` datetime DEFAULT CURRENT_TIMESTAMP,
  `CreatedBy` varchar(255) DEFAULT NULL,
  `LastUpdatedOn` datetime DEFAULT NULL,
  `LastUpdatedBy` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `DescriptionID` (`DescriptionID`),
  CONSTRAINT `tbl_subject_ibfk_1` FOREIGN KEY (`DescriptionID`) REFERENCES `tbl_description` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_subject`
--

LOCK TABLES `tbl_subject` WRITE;
/*!40000 ALTER TABLE `tbl_subject` DISABLE KEYS */;
INSERT INTO `tbl_subject` VALUES (1,'Florida','Curriculum',NULL,NULL,_binary '','2025-07-28 14:46:22','ManualInsert',NULL,NULL),(2,'Florida','Curriculum',NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL);
/*!40000 ALTER TABLE `tbl_subject` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_theme`
--

DROP TABLE IF EXISTS `tbl_theme`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_theme` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `ThemeName` varchar(50) NOT NULL,
  `Description` text,
  `CreatedOn` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `CreatedBy` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ThemeName` (`ThemeName`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_theme`
--

LOCK TABLES `tbl_theme` WRITE;
/*!40000 ALTER TABLE `tbl_theme` DISABLE KEYS */;
INSERT INTO `tbl_theme` VALUES (1,'Detective',NULL,'2025-07-28 21:32:21','System'),(2,'Fantasy',NULL,'2025-07-28 21:32:21','System'),(3,'Indian Epics',NULL,'2025-07-28 21:32:21','System');
/*!40000 ALTER TABLE `tbl_theme` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_topic`
--

DROP TABLE IF EXISTS `tbl_topic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_topic` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `SubjectID` int DEFAULT NULL,
  `TopicName` varchar(255) NOT NULL,
  `DescriptionID` int DEFAULT NULL,
  `SequenceNo` int DEFAULT NULL,
  `SummaryDescriptionID` int DEFAULT NULL,
  `ParentTopicID` int DEFAULT NULL,
  `Active` bit(1) DEFAULT b'1',
  `CreatedOn` datetime DEFAULT CURRENT_TIMESTAMP,
  `CreatedBy` varchar(255) DEFAULT NULL,
  `LastUpdatedOn` datetime DEFAULT NULL,
  `LastUpdatedBy` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `SubjectID` (`SubjectID`),
  KEY `DescriptionID` (`DescriptionID`),
  KEY `SummaryDescriptionID` (`SummaryDescriptionID`),
  KEY `ParentTopicID` (`ParentTopicID`),
  CONSTRAINT `tbl_topic_ibfk_1` FOREIGN KEY (`SubjectID`) REFERENCES `tbl_subject` (`ID`),
  CONSTRAINT `tbl_topic_ibfk_2` FOREIGN KEY (`DescriptionID`) REFERENCES `tbl_description` (`ID`),
  CONSTRAINT `tbl_topic_ibfk_3` FOREIGN KEY (`SummaryDescriptionID`) REFERENCES `tbl_description` (`ID`),
  CONSTRAINT `tbl_topic_ibfk_4` FOREIGN KEY (`ParentTopicID`) REFERENCES `tbl_topic` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=353 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_topic`
--

LOCK TABLES `tbl_topic` WRITE;
/*!40000 ALTER TABLE `tbl_topic` DISABLE KEYS */;
INSERT INTO `tbl_topic` VALUES (1,1,'Place Value Concepts',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:22','ManualInsert',NULL,NULL),(2,1,'Express How Digit Value Changes',NULL,NULL,NULL,1,_binary '','2025-07-28 14:46:22','ManualInsert',NULL,NULL),(3,2,'Place Value Concepts',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(4,2,'Read and Write Multi-Digit Numbers',NULL,NULL,NULL,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(5,2,'Plot, Order, and Compare Multi-Digit Numbers',NULL,NULL,NULL,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(6,2,'Round Whole Numbers',NULL,NULL,NULL,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(7,2,'Plot, Order, and Compare Decimals',NULL,NULL,NULL,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(8,2,'Multiplication and Division',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(9,2,'Recall Multiplication and Division Facts',NULL,NULL,NULL,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(10,2,'Multiply 3-digit by 2-digit Numbers',NULL,NULL,NULL,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(11,2,'Multiply 2-digit by 2-digit Numbers (Standard Algorithm)',NULL,NULL,NULL,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(12,2,'Divide 4-digit by 1-digit Numbers (with Remainders)',NULL,NULL,NULL,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(13,2,'Estimate Products and Quotients',NULL,NULL,NULL,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(14,2,'Decimal Operations',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(15,2,'Find One-Tenth/One-Hundredth More or Less',NULL,NULL,NULL,14,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(16,2,'Explore Adding and Subtracting Decimals to Hundredths',NULL,NULL,NULL,14,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(17,2,'Fractions and Decimals',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(18,2,'Model Equivalent Fractions (Tenths to Hundredths)',NULL,NULL,NULL,17,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(19,2,'Use Decimal Notation for Fractions',NULL,NULL,NULL,17,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(20,2,'Identify and Generate Equivalent Fractions',NULL,NULL,NULL,17,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(21,2,'Plot, Order, and Compare Fractions',NULL,NULL,NULL,17,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(22,2,'Operations with Fractions',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(23,2,'Decompose Fractions',NULL,NULL,NULL,22,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(24,2,'Add and Subtract Fractions with Like Denominators',NULL,NULL,NULL,22,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(25,2,'Add Fractions with Denominators of 10 and 100',NULL,NULL,NULL,22,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(26,2,'Multiply a Fraction by a Whole Number',NULL,NULL,NULL,22,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(27,2,'Algebraic Problem Solving',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(28,2,'Solve Real-World Multiplication & Division Problems',NULL,NULL,NULL,27,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(29,2,'Solve Real-World Fraction Addition & Subtraction Problems',NULL,NULL,NULL,27,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(30,2,'Solve Real-World Fraction Multiplication Problems',NULL,NULL,NULL,27,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(31,2,'Equations and Equality',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(32,2,'Determine if an Equation is True or False',NULL,NULL,NULL,31,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(33,2,'Write Equations to Determine an Unknown Number',NULL,NULL,NULL,31,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(34,2,'Factors and Patterns',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(35,2,'Determine Factor Pairs, Prime, and Composite Numbers',NULL,NULL,NULL,34,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(36,2,'Generate and Describe Numerical Patterns',NULL,NULL,NULL,34,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(37,2,'Measurement',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(38,2,'Select and Use Appropriate Measurement Tools',NULL,NULL,NULL,37,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(39,2,'Convert Within a Single System of Measurement',NULL,NULL,NULL,37,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(40,2,'Time and Money',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(41,2,'Solve Two-Step Problems Involving Time',NULL,NULL,NULL,40,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(42,2,'Solve Problems Involving Money with Decimals',NULL,NULL,NULL,40,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(43,2,'Geometric Reasoning: Angles',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(44,2,'Identify and Classify Angles',NULL,NULL,NULL,43,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(45,2,'Measure and Draw Angles with a Protractor',NULL,NULL,NULL,43,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(46,2,'Solve Problems with Unknown Angle Measures',NULL,NULL,NULL,43,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(47,2,'Geometric Reasoning: Area & Perimeter',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(48,2,'Solve Perimeter and Area Problems for Rectangles',NULL,NULL,NULL,47,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(49,2,'Compare Rectangles with Same Perimeter or Area',NULL,NULL,NULL,47,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(50,2,'Data Analysis',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(51,2,'Collect and Represent Numerical Data (Plots, Tables)',NULL,NULL,NULL,50,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(52,2,'Determine Mode, Median, or Range to Interpret Data',NULL,NULL,NULL,50,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(53,2,'Solve Real-World Problems Using Data',NULL,NULL,NULL,50,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(54,2,'Place Value with Decimals',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(55,2,'Express How Digit Value Changes (with Decimals)',NULL,NULL,NULL,54,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(56,2,'Read and Write Numbers with Decimals to Thousandths',NULL,NULL,NULL,54,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(57,2,'Compose and Decompose Numbers with Decimals',NULL,NULL,NULL,54,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(58,2,'Plot, Order, and Compare Numbers with Decimals',NULL,NULL,NULL,54,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(59,2,'Round Numbers with Decimals',NULL,NULL,NULL,54,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(60,2,'Whole Number Operations',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(61,2,'Multiply Multi-Digit Whole Numbers (Standard Algorithm)',NULL,NULL,NULL,60,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(62,2,'Divide Multi-Digit Whole Numbers (Standard Algorithm)',NULL,NULL,NULL,60,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(63,2,'Add and Subtract Multi-Digit Numbers with Decimals',NULL,NULL,NULL,14,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(64,2,'Explore Multiplying and Dividing Decimals (Estimation)',NULL,NULL,NULL,14,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(65,2,'Multiply/Divide Decimals by One-Tenth & One-Hundredth',NULL,NULL,NULL,14,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(66,2,'Understanding Fractions',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(67,2,'Represent Division of Whole Numbers as a Fraction',NULL,NULL,NULL,66,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(68,2,'Add and Subtract Fractions with Unlike Denominators',NULL,NULL,NULL,22,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(69,2,'Multiply a Fraction by a Fraction',NULL,NULL,NULL,22,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(70,2,'Predict the Size of a Product when Multiplying by a Fraction',NULL,NULL,NULL,22,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(71,2,'Explore Dividing Unit Fractions and Whole Numbers',NULL,NULL,NULL,22,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(72,2,'Solve Multi-Step Word Problems (Whole Numbers)',NULL,NULL,NULL,27,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(73,2,'Solve Word Problems (Fraction Addition/Subtraction/Multiplication)',NULL,NULL,NULL,27,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(74,2,'Solve Word Problems (Fraction Division)',NULL,NULL,NULL,27,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(75,2,'Expressions and Equations',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(76,2,'Translate Between Written Descriptions and Numerical Expressions',NULL,NULL,NULL,75,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(77,2,'Evaluate Expressions Using Order of Operations',NULL,NULL,NULL,75,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(78,2,'Determine if an Equation is True or False',NULL,NULL,NULL,75,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(79,2,'Write Equations to Find an Unknown Number',NULL,NULL,NULL,75,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(80,2,'Patterns and Relationships',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(81,2,'Identify and Write a Rule for a Numerical Pattern',NULL,NULL,NULL,80,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(82,2,'Use a Table to Record Inputs and Outputs for a Rule',NULL,NULL,NULL,80,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(83,2,'Measurement and Money',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(84,2,'Solve Problems Involving Measurement Conversions',NULL,NULL,NULL,83,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(85,2,'Solve Multi-Step Word Problems Involving Money',NULL,NULL,NULL,83,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(86,2,'Classifying 2D and 3D Figures',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(87,2,'Classify Triangles and Quadrilaterals by Attributes',NULL,NULL,NULL,86,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(88,2,'Identify and Classify 3D Figures by Attributes',NULL,NULL,NULL,86,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(89,2,'Perimeter and Area',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(90,2,'Find Perimeter and Area with Fractional/Decimal Sides',NULL,NULL,NULL,89,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(91,2,'Volume',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(92,2,'Explore Volume by Packing with Unit Cubes',NULL,NULL,NULL,91,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(93,2,'Find Volume of Rectangular Prisms Using a Formula',NULL,NULL,NULL,91,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(94,2,'Solve Word Problems Involving Volume',NULL,NULL,NULL,91,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(95,2,'The Coordinate Plane',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(96,2,'Identify Axes and Plot Ordered Pairs in the First Quadrant',NULL,NULL,NULL,95,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(97,2,'Represent and Interpret Problems on the Coordinate Plane',NULL,NULL,NULL,95,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(98,2,'Collect and Represent Data (Line Graphs, Line Plots)',NULL,NULL,NULL,50,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(99,2,'Interpret Data by Finding Mean, Mode, Median, or Range',NULL,NULL,NULL,50,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(100,2,'Rational Numbers',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(101,2,'Plot, Order, and Compare Rational Numbers',NULL,NULL,NULL,100,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(102,2,'Represent Quantities with Opposite Directions',NULL,NULL,NULL,100,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(103,2,'Understand and Find Absolute Value',NULL,NULL,NULL,100,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(104,2,'Solve Problems Involving Absolute Value',NULL,NULL,NULL,100,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(105,2,'Operations with Positive Rational Numbers',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(106,2,'Multiply and Divide Multi-Digit Decimals',NULL,NULL,NULL,105,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(107,2,'Multiply and Divide Positive Fractions',NULL,NULL,NULL,105,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(108,2,'Solve Multi-Step Problems with Decimals or Fractions',NULL,NULL,NULL,105,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(109,2,'Equivalent Forms of Numbers',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(110,2,'Find GCF and LCM',NULL,NULL,NULL,109,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(111,2,'Rewrite Sums Using the Distributive Property',NULL,NULL,NULL,109,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(112,2,'Evaluate Numbers with Natural Number Exponents',NULL,NULL,NULL,109,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(113,2,'Express Numbers as a Product of Prime Factors',NULL,NULL,NULL,109,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(114,2,'Convert Between Fractions, Decimals, and Percentages',NULL,NULL,NULL,109,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(115,2,'Operations with Integers',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(116,2,'Add and Subtract Integers',NULL,NULL,NULL,115,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(117,2,'Multiply and Divide Integers',NULL,NULL,NULL,115,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(118,2,'Algebraic Expressions',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(119,2,'Translate Between Written Descriptions and Algebraic Expressions',NULL,NULL,NULL,118,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(120,2,'Write and Represent Inequalities on a Number Line',NULL,NULL,NULL,118,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(121,2,'Evaluate Algebraic Expressions',NULL,NULL,NULL,118,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(122,2,'Generate Equivalent Algebraic Expressions',NULL,NULL,NULL,118,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(123,2,'Equations and Inequalities',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(124,2,'Determine Values That Make Equations/Inequalities True',NULL,NULL,NULL,123,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(125,2,'Write and Solve One-Step Equations (Addition/Subtraction)',NULL,NULL,NULL,123,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(126,2,'Write and Solve One-Step Equations (Multiplication/Division)',NULL,NULL,NULL,123,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(127,2,'Find Unknowns in Equations with Decimals or Fractions',NULL,NULL,NULL,123,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(128,2,'Ratios and Rates',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(129,2,'Write and Interpret Ratios',NULL,NULL,NULL,128,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(130,2,'Determine and Interpret Unit Rates',NULL,NULL,NULL,128,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(131,2,'Use Tables to Display Equivalent Ratios',NULL,NULL,NULL,128,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(132,2,'Apply Ratios to Solve Percent Problems',NULL,NULL,NULL,128,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(133,2,'Solve Problems Involving Ratios, Rates, and Conversions',NULL,NULL,NULL,128,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(134,2,'Plot Rational Numbers in All Four Quadrants',NULL,NULL,NULL,95,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(135,2,'Find Distances Between Ordered Pairs',NULL,NULL,NULL,95,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(136,2,'Solve Problems by Plotting Points (Perimeter, Area)',NULL,NULL,NULL,95,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(137,2,'Area and Volume',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(138,2,'Find the Area of Triangles',NULL,NULL,NULL,137,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(139,2,'Find the Area of Quadrilaterals and Composite Figures',NULL,NULL,NULL,137,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(140,2,'Find the Volume of Right Rectangular Prisms',NULL,NULL,NULL,137,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(141,2,'Surface Area',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(142,2,'Find the Surface Area of Prisms and Pyramids Using Nets',NULL,NULL,NULL,141,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(143,2,'Statistical Questions',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(144,2,'Formulate a Statistical Question',NULL,NULL,NULL,143,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(145,2,'Find and Interpret Mean, Median, Mode, and Range',NULL,NULL,NULL,50,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(146,2,'Interpret Box Plots',NULL,NULL,NULL,50,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(147,2,'Describe and Interpret Data Distribution (Histograms/Line Plots)',NULL,NULL,NULL,50,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(148,2,'Create Box Plots and Histograms',NULL,NULL,NULL,50,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(149,2,'Analyze How Changes in Data Impact Measures of Center/Variation',NULL,NULL,NULL,50,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(150,2,'Exponents and Rational Numbers',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(151,2,'Apply Laws of Exponents to Numerical Expressions',NULL,NULL,NULL,150,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(152,2,'Rewrite Rational Numbers in Equivalent Forms',NULL,NULL,NULL,150,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(153,2,'Operations with Rational Numbers',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(154,2,'Solve Multi-Step Problems with Order of Operations',NULL,NULL,NULL,153,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(155,2,'Add, Subtract, Multiply, and Divide Rational Numbers',NULL,NULL,NULL,153,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(156,2,'Solve Real-World Problems with Rational Numbers',NULL,NULL,NULL,153,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(157,2,'Linear Expressions',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(158,2,'Add and Subtract Linear Expressions',NULL,NULL,NULL,157,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(159,2,'Determine if Two Linear Expressions are Equivalent',NULL,NULL,NULL,157,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(160,2,'Write and Solve One-Step Inequalities',NULL,NULL,NULL,123,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(161,2,'Write and Solve Two-Step Equations',NULL,NULL,NULL,123,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(162,2,'Proportional Reasoning',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(163,2,'Solve Multi-Step Real-World Percent Problems',NULL,NULL,NULL,162,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(164,2,'Solve Real-World Problems Involving Proportions',NULL,NULL,NULL,162,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(165,2,'Solve Problems Involving Unit Conversions',NULL,NULL,NULL,162,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(166,2,'Proportional Relationships',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(167,2,'Determine if a Proportional Relationship Exists',NULL,NULL,NULL,166,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(168,2,'Determine the Constant of Proportionality',NULL,NULL,NULL,166,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(169,2,'Graph Proportional Relationships',NULL,NULL,NULL,166,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(170,2,'Translate Between Representations of Proportional Relationships',NULL,NULL,NULL,166,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(171,2,'Solve Real-World Problems with Proportional Relationships',NULL,NULL,NULL,166,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(172,2,'2D Geometry',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(173,2,'Find the Area of Trapezoids, Parallelograms, and Rhombi',NULL,NULL,NULL,172,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(174,2,'Find the Area of Polygons and Composite Figures',NULL,NULL,NULL,172,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(175,2,'2D Geometry (Circles)',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(176,2,'Find the Circumference of a Circle',NULL,NULL,NULL,175,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(177,2,'Find the Area of a Circle',NULL,NULL,NULL,175,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(178,2,'2D Geometry (Scale Drawings)',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(179,2,'Solve Problems with Scale Drawings and Scale Factors',NULL,NULL,NULL,178,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(180,2,'3D Geometry (Cylinders)',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(181,2,'Find the Surface Area of a Right Circular Cylinder',NULL,NULL,NULL,180,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(182,2,'Solve Real-World Problems with Surface Area of Cylinders',NULL,NULL,NULL,180,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(183,2,'Solve Real-World Problems with Volume of Cylinders',NULL,NULL,NULL,180,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(184,2,'Data Interpretation',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(185,2,'Choose Appropriate Measures of Center or Variation',NULL,NULL,NULL,184,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(186,2,'Compare Two Populations Using Measures of Center/Variability',NULL,NULL,NULL,184,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(187,2,'Make Predictions About a Population from a Sample',NULL,NULL,NULL,184,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(188,2,'Construct and Interpret Circle Graphs',NULL,NULL,NULL,184,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(189,2,'Choose and Create Appropriate Graphical Representations',NULL,NULL,NULL,184,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(190,2,'Probability',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(191,2,'Determine the Sample Space of an Experiment',NULL,NULL,NULL,190,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(192,2,'Interpret the Likelihood of an Event',NULL,NULL,NULL,190,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(193,2,'Find the Theoretical Probability of an Event',NULL,NULL,NULL,190,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(194,2,'Compare Experimental and Theoretical Probabilities',NULL,NULL,NULL,190,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(195,2,'Real Numbers',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(196,2,'Define and Locate Irrational Numbers',NULL,NULL,NULL,195,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(197,2,'Plot, Order, and Compare Rational and Irrational Numbers',NULL,NULL,NULL,195,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(198,2,'Exponents and Scientific Notation',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(199,2,'Apply Laws of Exponents (Integer Exponents)',NULL,NULL,NULL,198,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(200,2,'Express Numbers in Scientific Notation',NULL,NULL,NULL,198,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(201,2,'Add, Subtract, Multiply, and Divide in Scientific Notation',NULL,NULL,NULL,198,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(202,2,'Solve Real-World Problems with Scientific Notation',NULL,NULL,NULL,198,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(203,2,'Radicals and Order of Operations',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(204,2,'Solve Multi-Step Problems with Exponents and Radicals',NULL,NULL,NULL,203,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(205,2,'Apply Laws of Exponents to Algebraic Expressions',NULL,NULL,NULL,118,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(206,2,'Multiply Two Linear Expressions',NULL,NULL,NULL,118,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(207,2,'Factor a Common Monomial from an Expression',NULL,NULL,NULL,118,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(208,2,'Linear Equations and Inequalities',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(209,2,'Solve Multi-Step Linear Equations',NULL,NULL,NULL,208,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(210,2,'Solve Two-Step Linear Inequalities',NULL,NULL,NULL,208,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(211,2,'Square and Cube Roots',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(212,2,'Solve Equations of the Form x┬▓ = p and x┬│ = q',NULL,NULL,NULL,211,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(213,2,'Linear Relationships',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(214,2,'Determine if a Linear Relationship is Proportional',NULL,NULL,NULL,213,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(215,2,'Determine the Slope of a Linear Relationship',NULL,NULL,NULL,213,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(216,2,'Write an Equation in Slope-Intercept Form',NULL,NULL,NULL,213,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(217,2,'Graph a Two-Variable Linear Equation',NULL,NULL,NULL,213,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(218,2,'Determine and Interpret Slope and y-intercept',NULL,NULL,NULL,213,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(219,2,'Systems of Equations',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(220,2,'Identify Solutions to a System of Two Linear Equations',NULL,NULL,NULL,219,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(221,2,'Determine the Number of Solutions by Graphing',NULL,NULL,NULL,219,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(222,2,'Solve Systems of Two Linear Equations by Graphing',NULL,NULL,NULL,219,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(223,2,'Functions',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(224,2,'Determine if a Relation is a Function; Find Domain/Range',NULL,NULL,NULL,223,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(225,2,'Determine if a Function is Linear',NULL,NULL,NULL,223,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(226,2,'Analyze where a Function is Increasing, Decreasing, or Constant',NULL,NULL,NULL,223,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(227,2,'Pythagorean Theorem',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(228,2,'Apply the Pythagorean Theorem to Find Unknown Side Lengths',NULL,NULL,NULL,227,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(229,2,'Apply the Pythagorean Theorem to Find Distance on a Coordinate Plane',NULL,NULL,NULL,227,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(230,2,'Triangles',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(231,2,'Use Triangle Inequality and Converse of Pythagorean Theorem',NULL,NULL,NULL,230,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(232,2,'Angles',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(233,2,'Solve Problems with Supplementary, Complementary, Vertical, Adjacent Angles',NULL,NULL,NULL,232,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(234,2,'Solve Problems with Interior and Exterior Angles of a Triangle',NULL,NULL,NULL,232,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(235,2,'Find Sums of Interior Angles of Regular Polygons',NULL,NULL,NULL,232,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(236,2,'Transformations',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(237,2,'Identify a Single Transformation (Reflection, Translation, Rotation)',NULL,NULL,NULL,236,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(238,2,'Identify the Scale Factor of a Dilation',NULL,NULL,NULL,236,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(239,2,'Describe the Effect of a Single Transformation on Coordinates',NULL,NULL,NULL,236,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(240,2,'Similar Triangles',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(241,2,'Solve Problems Involving Similar Triangles',NULL,NULL,NULL,240,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(242,2,'Bivariate Data',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(243,2,'Construct a Scatter Plot or Line Graph',NULL,NULL,NULL,242,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(244,2,'Describe Patterns of Association in a Scatter Plot',NULL,NULL,NULL,242,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(245,2,'Informally Fit a Straight Line to a Scatter Plot',NULL,NULL,NULL,242,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(246,2,'Repeated Experiments',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(247,2,'Determine the Sample Space for a Repeated Experiment',NULL,NULL,NULL,246,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(248,2,'Find the Theoretical Probability of a Repeated Experiment',NULL,NULL,NULL,246,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(249,2,'Solve Problems and Make Predictions Based on Probability',NULL,NULL,NULL,246,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(250,2,'Exponents and Radicals',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(251,2,'Apply Laws of Exponents with Rational Exponents',NULL,NULL,NULL,250,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(252,2,'Generate Equivalent Algebraic Expressions Using Exponents',NULL,NULL,NULL,250,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(253,2,'Add, Subtract, Multiply, and Divide Numerical Radicals',NULL,NULL,NULL,250,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(254,2,'Identify and Interpret Parts of an Equation or Expression',NULL,NULL,NULL,118,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(255,2,'Rearrange Equations or Formulas to Isolate a Quantity',NULL,NULL,NULL,118,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(256,2,'Polynomials',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(257,2,'Add, Subtract, and Multiply Polynomial Expressions',NULL,NULL,NULL,256,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(258,2,'Divide a Polynomial by a Monomial',NULL,NULL,NULL,256,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(259,2,'Rewrite a Polynomial as a Product of Polynomials (Factoring)',NULL,NULL,NULL,256,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(260,2,'Linear Equations and Functions',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(261,2,'Write and Solve One-Variable Multi-Step Linear Equations',NULL,NULL,NULL,260,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(262,2,'Write Linear Two-Variable Equations',NULL,NULL,NULL,260,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(263,2,'Write Equations for Parallel or Perpendicular Lines',NULL,NULL,NULL,260,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(264,2,'Graph and Interpret Key Features of Linear Functions',NULL,NULL,NULL,260,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(265,2,'Solve and Graph Real-World Problems Modeled with Linear Functions',NULL,NULL,NULL,260,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(266,2,'Linear Inequalities',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(267,2,'Write and Solve One-Variable Linear Inequalities',NULL,NULL,NULL,266,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(268,2,'Write Two-Variable Linear Inequalities',NULL,NULL,NULL,266,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(269,2,'Graph the Solution Set to a Two-Variable Linear Inequality',NULL,NULL,NULL,266,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(270,2,'Quadratic Equations and Functions',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(271,2,'Write and Solve One-Variable Quadratic Equations',NULL,NULL,NULL,270,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(272,2,'Write a Quadratic Function from a Graph, Description, or Table',NULL,NULL,NULL,270,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(273,2,'Write a Quadratic Equation Given x-intercepts and a Point',NULL,NULL,NULL,270,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(274,2,'Determine and Interpret the Vertex and Zeros of a Quadratic',NULL,NULL,NULL,270,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(275,2,'Graph and Interpret Key Features of Quadratic Functions',NULL,NULL,NULL,270,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(276,2,'Solve and Graph Real-World Problems Modeled with Quadratic Functions',NULL,NULL,NULL,270,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(277,2,'Absolute Value Functions',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(278,2,'Write and Solve One-Variable Absolute Value Equations',NULL,NULL,NULL,277,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(279,2,'Graph and Determine Key Features of Absolute Value Functions',NULL,NULL,NULL,277,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(280,2,'Exponential Functions',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(281,2,'Classify an Exponential Function as Growth or Decay',NULL,NULL,NULL,280,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(282,2,'Write an Exponential Function from a Graph, Description, or Table',NULL,NULL,NULL,280,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(283,2,'Graph and Determine Key Features of Exponential Functions',NULL,NULL,NULL,280,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(284,2,'Systems of Equations and Inequalities',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(285,2,'Write and Solve a System of Two-Variable Linear Equations',NULL,NULL,NULL,284,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(286,2,'Graph the Solution Set of a System of Two-Variable Linear Inequalities',NULL,NULL,NULL,284,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(287,2,'Represent Constraints as Systems of Equations or Inequalities',NULL,NULL,NULL,284,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(288,2,'Classify a Function Type from an Equation, Graph, or Table',NULL,NULL,NULL,223,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(289,2,'Evaluate a Function and Interpret the Output',NULL,NULL,NULL,223,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(290,2,'Calculate and Interpret the Average Rate of Change',NULL,NULL,NULL,223,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(291,2,'Compare Key Features of Linear Functions',NULL,NULL,NULL,223,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(292,2,'Compare Key Features of Linear and Nonlinear Functions',NULL,NULL,NULL,223,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(293,2,'Determine if a Linear, Quadratic, or Exponential Function Best Models a Situation',NULL,NULL,NULL,223,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(294,2,'Transformations of Functions',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(295,2,'Identify the Effect of Transformations on a Function\'s Graph',NULL,NULL,NULL,294,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(296,2,'Financial Literacy',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(297,2,'Solve Real-World Problems Involving Simple and Compound Interest',NULL,NULL,NULL,296,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(298,2,'Explain the Relationship Between Interest and Growth (Linear/Exponential)',NULL,NULL,NULL,296,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(299,2,'Select an Appropriate Method to Represent Data',NULL,NULL,NULL,50,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(300,2,'Interpret Data Distributions',NULL,NULL,NULL,50,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(301,2,'Explain the Difference Between Correlation and Causation',NULL,NULL,NULL,50,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(302,2,'Estimate a Population Metric and Use Margin of Error',NULL,NULL,NULL,50,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(303,2,'Fit a Linear Function to Data and Interpret the Model',NULL,NULL,NULL,242,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(304,2,'Determine Correlation Strength and Direction from a Scatter Plot',NULL,NULL,NULL,242,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(305,2,'Categorical Data',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(306,2,'Construct and Interpret a Two-Way Frequency Table',NULL,NULL,NULL,305,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(307,2,'Geometric Proofs (Lines and Angles)',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(308,2,'Prove and Apply Theorems about Lines and Angles',NULL,NULL,NULL,307,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(309,2,'Geometric Proofs (Triangles)',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(310,2,'Prove Triangle Congruence or Similarity',NULL,NULL,NULL,309,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(311,2,'Prove and Apply Theorems about Triangles',NULL,NULL,NULL,309,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(312,2,'Geometric Proofs (Quadrilaterals)',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(313,2,'Prove and Apply Theorems about Parallelograms',NULL,NULL,NULL,312,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(314,2,'Prove and Apply Theorems about Trapezoids',NULL,NULL,NULL,312,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(315,2,'Congruence and Similarity',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(316,2,'Solve Problems Involving Congruence or Similarity',NULL,NULL,NULL,315,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(317,2,'Describe and Represent Transformations Algebraically',NULL,NULL,NULL,236,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(318,2,'Identify Transformations that Preserve Distance (Rigid Motion)',NULL,NULL,NULL,236,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(319,2,'Identify a Sequence of Transformations to Map Figures',NULL,NULL,NULL,236,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(320,2,'Draw a Transformed Figure on a Coordinate Plane',NULL,NULL,NULL,236,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(321,2,'Apply Rigid Transformations to Justify Congruence',NULL,NULL,NULL,236,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(322,2,'Apply Transformations to Justify Similarity',NULL,NULL,NULL,236,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(323,2,'Coordinate Geometry',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(324,2,'Determine the Weighted Average of Points on a Line',NULL,NULL,NULL,323,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(325,2,'Classify Figures Using Coordinate Geometry',NULL,NULL,NULL,323,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(326,2,'Solve Geometric Problems Involving Lines, Circles, Triangles, Quadrilaterals',NULL,NULL,NULL,323,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(327,2,'Solve Problems Involving Perimeter or Area on the Coordinate Plane',NULL,NULL,NULL,323,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(328,2,'2D and 3D Figures',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(329,2,'Identify Shapes of 2D Cross-Sections of 3D Figures',NULL,NULL,NULL,328,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(330,2,'Identify 3D Objects Generated by Rotations of 2D Figures',NULL,NULL,NULL,328,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(331,2,'Determine How Dilations Affect Area, Surface Area, and Volume',NULL,NULL,NULL,37,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(332,2,'Solve Problems Involving the Area of 2D Figures',NULL,NULL,NULL,37,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(333,2,'Solve Problems Involving the Volume of 3D Figures',NULL,NULL,NULL,37,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(334,2,'Solve Problems Involving the Surface Area of 3D Figures',NULL,NULL,NULL,37,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(335,2,'Geometric Constructions',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(336,2,'Construct a Copy of a Segment or an Angle',NULL,NULL,NULL,335,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(337,2,'Construct the Bisector of a Segment or an Angle',NULL,NULL,NULL,335,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(338,2,'Construct Inscribed and Circumscribed Circles of a Triangle',NULL,NULL,NULL,335,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(339,2,'Circles',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(340,2,'Solve Problems Involving Lengths of Secants, Tangents, and Chords',NULL,NULL,NULL,339,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(341,2,'Solve Problems Involving Arc Measures and Related Angles',NULL,NULL,NULL,339,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(342,2,'Solve Problems Involving Triangles and Quadrilaterals Inscribed in a Circle',NULL,NULL,NULL,339,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(343,2,'Solve Problems Involving Arc Length and Area of a Sector',NULL,NULL,NULL,339,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(344,2,'Equations of Circles',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(345,2,'Derive and Create the Equation of a Circle',NULL,NULL,NULL,344,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(346,2,'Graph and Solve Problems Modeled with an Equation of a Circle',NULL,NULL,NULL,344,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(347,2,'Right Triangle Trigonometry',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(348,2,'Define Trigonometric Ratios for Acute Angles',NULL,NULL,NULL,347,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(349,2,'Solve Problems Using Trigonometric Ratios and Pythagorean Theorem',NULL,NULL,NULL,347,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(350,2,'Logic',NULL,NULL,NULL,NULL,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(351,2,'Interpret Conditional Statements and Find Converse, Inverse, Contrapositive',NULL,NULL,NULL,350,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(352,2,'Judge the Validity of Arguments and Give Counterexamples',NULL,NULL,NULL,350,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL);
/*!40000 ALTER TABLE `tbl_topic` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_topicgrade`
--

DROP TABLE IF EXISTS `tbl_topicgrade`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_topicgrade` (
  `TopicID` int NOT NULL,
  `GradeID` int NOT NULL,
  `Active` bit(1) DEFAULT b'1',
  `CreatedOn` datetime DEFAULT CURRENT_TIMESTAMP,
  `CreatedBy` varchar(255) DEFAULT NULL,
  `LastUpdatedOn` datetime DEFAULT NULL,
  `LastUpdatedBy` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`TopicID`,`GradeID`),
  KEY `GradeID` (`GradeID`),
  CONSTRAINT `tbl_topicgrade_ibfk_1` FOREIGN KEY (`TopicID`) REFERENCES `tbl_topic` (`ID`),
  CONSTRAINT `tbl_topicgrade_ibfk_2` FOREIGN KEY (`GradeID`) REFERENCES `tbl_grade` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_topicgrade`
--

LOCK TABLES `tbl_topicgrade` WRITE;
/*!40000 ALTER TABLE `tbl_topicgrade` DISABLE KEYS */;
INSERT INTO `tbl_topicgrade` VALUES (2,1,_binary '','2025-07-28 14:46:22','ManualInsert',NULL,NULL),(4,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(5,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(6,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(7,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(9,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(10,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(11,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(12,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(13,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(15,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(16,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(18,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(19,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(20,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(21,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(23,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(24,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(25,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(26,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(28,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(29,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(30,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(32,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(33,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(35,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(36,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(38,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(39,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(41,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(42,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(44,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(45,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(46,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(48,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(49,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(51,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(52,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(53,2,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(55,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(56,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(57,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(58,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(59,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(61,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(62,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(63,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(64,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(65,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(67,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(68,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(69,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(70,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(71,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(72,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(73,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(74,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(76,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(77,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(78,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(79,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(81,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(82,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(84,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(85,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(87,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(88,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(90,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(92,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(93,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(94,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(96,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(97,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(98,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(99,3,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(101,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(102,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(103,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(104,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(106,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(107,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(108,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(110,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(111,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(112,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(113,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(114,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(116,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(117,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(119,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(120,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(121,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(122,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(124,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(125,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(126,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(127,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(129,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(130,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(131,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(132,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(133,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(134,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(135,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(136,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(138,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(139,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(140,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(142,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(144,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(145,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(146,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(147,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(148,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(149,4,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(151,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(152,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(154,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(155,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(156,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(158,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(159,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(160,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(161,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(163,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(164,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(165,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(167,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(168,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(169,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(170,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(171,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(173,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(174,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(176,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(177,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(179,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(181,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(182,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(183,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(185,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(186,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(187,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(188,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(189,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(191,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(192,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(193,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(194,5,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(196,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(197,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(199,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(200,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(201,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(202,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(204,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(205,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(206,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(207,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(209,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(210,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(212,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(214,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(215,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(216,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(217,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(218,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(220,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(221,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(222,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(224,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(225,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(226,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(228,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(229,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(231,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(233,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(234,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(235,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(237,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(238,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(239,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(241,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(243,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(244,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(245,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(247,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(248,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(249,6,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(251,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(252,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(253,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(254,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(255,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(257,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(258,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(259,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(261,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(262,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(263,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(264,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(265,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(267,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(268,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(269,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(271,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(272,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(273,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(274,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(275,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(276,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(278,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(279,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(281,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(282,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(283,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(285,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(286,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(287,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(288,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(289,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(290,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(291,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(292,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(293,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(295,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(297,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(298,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(299,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(300,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(301,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(302,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(303,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(304,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(306,7,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(308,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(310,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(311,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(313,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(314,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(316,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(317,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(318,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(319,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(320,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(321,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(322,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(324,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(325,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(326,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(327,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(329,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(330,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(331,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(332,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(333,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(334,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(336,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(337,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(338,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(340,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(341,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(342,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(343,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(345,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(346,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(348,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(349,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(351,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL),(352,8,_binary '','2025-07-28 14:46:38','SEEDER',NULL,NULL);
/*!40000 ALTER TABLE `tbl_topicgrade` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_topictheme`
--

DROP TABLE IF EXISTS `tbl_topictheme`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_topictheme` (
  `TopicID` int NOT NULL,
  `ThemeID` int NOT NULL,
  `IsDefault` tinyint(1) DEFAULT '0',
  `CreatedOn` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `CreatedBy` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`TopicID`,`ThemeID`),
  KEY `ThemeID` (`ThemeID`),
  CONSTRAINT `tbl_topictheme_ibfk_1` FOREIGN KEY (`TopicID`) REFERENCES `tbl_topic` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `tbl_topictheme_ibfk_2` FOREIGN KEY (`ThemeID`) REFERENCES `tbl_theme` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_topictheme`
--

LOCK TABLES `tbl_topictheme` WRITE;
/*!40000 ALTER TABLE `tbl_topictheme` DISABLE KEYS */;
INSERT INTO `tbl_topictheme` VALUES (2,1,1,'2025-07-28 21:49:06','Admin'),(2,2,0,'2025-07-28 21:49:06','Admin'),(2,3,0,'2025-07-28 21:49:06','Admin');
/*!40000 ALTER TABLE `tbl_topictheme` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_user`
--

DROP TABLE IF EXISTS `tbl_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_user` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Username` varchar(50) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `PasswordHash` varchar(255) NOT NULL,
  `UserType` varchar(20) DEFAULT 'Student',
  `ParentUserID` int DEFAULT NULL,
  `CreatedOn` datetime DEFAULT CURRENT_TIMESTAMP,
  `LastUpdatedOn` datetime DEFAULT NULL,
  `IsActive` bit(1) DEFAULT b'1',
  `ResetToken` varchar(100) DEFAULT NULL,
  `ResetTokenExpiry` datetime DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Username` (`Username`),
  UNIQUE KEY `Email` (`Email`),
  KEY `fk_parent_user` (`ParentUserID`),
  CONSTRAINT `fk_parent_user` FOREIGN KEY (`ParentUserID`) REFERENCES `tbl_user` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_user`
--

LOCK TABLES `tbl_user` WRITE;
/*!40000 ALTER TABLE `tbl_user` DISABLE KEYS */;
INSERT INTO `tbl_user` VALUES (4,'admin','admin@logicandstories.com','$2b$12$Z42uSceWiMkeEgf9zlJNp.qz78iTq87HCgyMtDdNhHL70qFk1fIby','Admin',NULL,'2025-07-27 19:22:51',NULL,_binary '',NULL,NULL),(8,'pooja','poojaa1253@gmail.com','$2b$12$3vd4OcEiYaasIismDkFAjOzC7YzGNzCxvoyBtvTnaayFCI1ObMpFC','Parent',NULL,'2025-07-28 17:19:41',NULL,_binary '',NULL,NULL),(9,'Vihaan','vihaan@logicandstories.student','$2b$12$iBfAHj/L4OrLbptrUGOqPeaccJmhv.F41nOR5hQc2KOW.5dwcKhPC','Student',8,'2025-07-28 17:20:18',NULL,_binary '',NULL,NULL),(10,'test','admin@bricks4tricks.com','$2b$12$FjXe60w9s9VhcuWUVFqpnOjfqlQwKcaTURzig5BXXWZjDT.SULAqe','Parent',NULL,'2025-07-28 19:25:33',NULL,_binary '','d00b5d7074b5b58b4f4431b01f2fe389cde2a2c566e0ef3c112d8ba9caa7c375','2025-07-28 20:28:28');
/*!40000 ALTER TABLE `tbl_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_userprogress`
--

DROP TABLE IF EXISTS `tbl_userprogress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_userprogress` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `UserID` int NOT NULL,
  `TopicID` int NOT NULL,
  `Status` enum('inProgress','completed') NOT NULL,
  `LastUpdated` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `CreatedOn` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `UserID` (`UserID`,`TopicID`),
  KEY `TopicID` (`TopicID`),
  CONSTRAINT `tbl_userprogress_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `tbl_user` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `tbl_userprogress_ibfk_2` FOREIGN KEY (`TopicID`) REFERENCES `tbl_topic` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_userprogress`
--

LOCK TABLES `tbl_userprogress` WRITE;
/*!40000 ALTER TABLE `tbl_userprogress` DISABLE KEYS */;
INSERT INTO `tbl_userprogress` VALUES (1,9,2,'completed','2025-07-28 21:51:56','2025-07-28 21:50:23');
/*!40000 ALTER TABLE `tbl_userprogress` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_usertopicdifficulty`
--

DROP TABLE IF EXISTS `tbl_usertopicdifficulty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_usertopicdifficulty` (
  `UserID` int NOT NULL,
  `TopicID` int NOT NULL,
  `CurrentDifficulty` int DEFAULT '1',
  `LastUpdatedOn` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`UserID`,`TopicID`),
  KEY `TopicID` (`TopicID`),
  CONSTRAINT `tbl_usertopicdifficulty_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `tbl_user` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `tbl_usertopicdifficulty_ibfk_2` FOREIGN KEY (`TopicID`) REFERENCES `tbl_topic` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_usertopicdifficulty`
--

LOCK TABLES `tbl_usertopicdifficulty` WRITE;
/*!40000 ALTER TABLE `tbl_usertopicdifficulty` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_usertopicdifficulty` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-29  2:01:55
