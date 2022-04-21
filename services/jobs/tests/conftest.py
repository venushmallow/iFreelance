import pytest

# designing the Integration Tests with temporary 'mysql' container
@pytest.fixture
def client():
    from src import app

    app.app.config['TESTING'] = True

    app.db.engine.execute('DROP TABLE IF EXISTS `job`;')

    app.db.engine.execute('''CREATE TABLE `job` (
      `job_id` int NOT NULL AUTO_INCREMENT,
      `title` varchar(64) NOT NULL,
      `description` mediumtext NOT NULL,
      `price` float NOT NULL,
      `seller_id` int NOT NULL,
      PRIMARY KEY (`job_id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8;''')

    app.db.engine.execute('''INSERT INTO `job` VALUES
      (1,'Design Portfolio Website','Design a professional website for your business.',40, 1),
      (2,'Party Wrecker','Hire my service to wreck any party you want to bail out from but forced to come.',60.5, 1),
      (3,'Babysit Children','Babysit your children at home.',18.7, 1),
      (7,'Do School Homework','Straight A confirmed.',25.55, 1),
      (9,'Free Therapy','Certified psychologist, free therapy since therapy prices are insane.',0, 1);''')

    return app.app.test_client()
