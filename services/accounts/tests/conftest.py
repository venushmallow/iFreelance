import pytest


@pytest.fixture
def client():
    from src import app

    app.app.config['TESTING'] = True
    
    app.db.engine.execute('DROP TABLE IF EXISTS `account`;')
    
    app.db.engine.execute('''CREATE TABLE `account` (
                          `account_id` int NOT NULL AUTO_INCREMENT,
                          `user_email` varchar(64) NOT NULL,
                          `password` varchar(100) NOT NULL,
                          `user_phone` varchar(10) NOT NULL,
                          PRIMARY KEY (`account_id`))
                          ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;''')

    return app.app.test_client()