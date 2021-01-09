drop table if exists usertable;
CREATE TABLE `usertable` (
  `UID` integer primary key,
  `name` varchar(30) NOT NULL,
  `profileID` varchar(20) DEFAULT NULL,
  `salary` int(9) DEFAULT NULL,
  `passportNr` varchar(20) DEFAULT NULL,
  `email` varchar(300) DEFAULT NULL,
  `nickName` varchar(300) DEFAULT NULL,
  `password` varchar(300) DEFAULT NULL
);



INSERT INTO `usertable` (`UID`, `name`, `profileID`, `salary`, `passportNr`, `email`, `nickName`, `password`) VALUES
    (1, 'Francois', '10', 250, '8605255014084', '', '', 'ccf4c101985e3bea45e7141af6be89308dbcc10f5763deb97b7d246c2dd9411c'),
    (2, 'Michandre', '11', 300, '9104154800081', '', '', '05842ffb6dc90bef3543dd85ee50dd302f3d1f163de1a76eee073ee97d851937'),
    (3, 'Colette', '12', 275, '8403024800086', '', '', 'c69d171e761fe56711e908515def631856c665dc234a0aa404b32c73bdbc81ac'),
    (4, 'Phillip', '13', 400, '8702245800084', '', '', 'b6efdfb0e20a34908c092725db15ae0c3666b3cea558fa74e0667bd91a10a0d3'),
    (5, 'Ivan', '14', 200, '8601185800080', '', '', 'be042a70c99d1c438cdcbd479b955e4fba33faf4f8c494239257e4248bbcf4ff'),
    (6, 'Admin', '99', 100, '8605255014084', '', '', '6ef110b045cbaa212258f7e5f08ed22216147594464427585871bfab9753ba25');