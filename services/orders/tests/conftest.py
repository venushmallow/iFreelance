import pytest


@pytest.fixture
def client():
    from src import app

    app.app.config['TESTING'] = True

    app.db.engine.execute('SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";')
    app.db.engine.execute('SET time_zone = "+00:00";')

    app.db.engine.execute('DROP TABLE IF EXISTS `order`;')
    app.db.engine.execute('''CREATE TABLE `order` (
      `order_id` int(11) NOT NULL AUTO_INCREMENT,
      `customer_email` varchar(64) NOT NULL,
      `customer_phone` int(10) NOT NULL,
      `seller_id` int(11) NOT NULL,
      `status` varchar(10) NOT NULL,
      `created` datetime NOT NULL,
      `job_id` int(11) NOT NULL,
      `title` varchar(64) NOT NULL,
      PRIMARY KEY (`order_id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;''')
    
    # app.db.engine.execute('DROP TABLE IF EXISTS `order_item`;')
    # app.db.engine.execute('''CREATE TABLE `order_item` (
    #   `item_id` int(11) NOT NULL AUTO_INCREMENT,
    #   `order_id` int(11) NOT NULL,
    #   `job_id` int(11) NOT NULL,
    #   PRIMARY KEY (`item_id`)
    # ) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;''')

    app.db.engine.execute('''INSERT INTO `order` (`order_id`, `customer_email`, `customer_phone`, `seller_id`, `status`, `created`, `job_id`, `title`) VALUES
      (5, 'cposkitt@smu.edu.sg', '88888888', 1, 'PENDING', '2021-08-10 00:00:00', 2, 'Party Wrecker'),
      (6, 'phris@coskitt.com', '99999999', 1, 'PENDING', '2021-08-10 00:00:00', 9, 'Free Therapy');''')

    # app.db.engine.execute('''INSERT INTO `order_item` (`item_id`, `order_id`, `job_id`) VALUES
    # (9, 5, 1),
    # (10, 5, 2),
    # (11, 6, 9);''')

    return app.app.test_client()
