CREATE TABLE `settings` (
    `id` int(4) NOT NULL AUTO_INCREMENT,
    `name` varchar(32) NOT NULL,
    `value` varchar(32) NOT NULL,

    `created_at` datetime NOT NULL DEFAULT current_timestamp(),
    `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
    PRIMARY KEY (`id`)
);


CREATE TABLE `users` (
    `id` int(16) NOT NULL AUTO_INCREMENT,
    `username` varchar(32) NOT NULL,
    `email` varchar(32) NOT NULL,
    `state` enum('pending','active','banned'),
    `firstname` varchar(32) NOT NULL,
    `lastname` varchar(32) NOT NULL,
    `role` enum('customer','supporter', 'admin'),

    `street` varchar(32) NOT NULL,
    `number` varchar(4) NOT NULL,
    `postcode` varchar(8) NOT NULL,
    `city` varchar(32) NOT NULL,
    `country` varchar(32) NOT NULL,

    `created_at` datetime NOT NULL DEFAULT current_timestamp(),
    `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
    PRIMARY KEY (`id`, `username`, `email`)
);

CREATE TABLE `auth` (
    `id` int(16) NOT NULL,
    `username` varchar(32) NOT NULL,
    `email` varchar(32) NOT NULL,
    `password` varchar(64) NOT NULL,
    FOREIGN KEY (`id`) REFERENCES users(`id`)
    FOREIGN KEY (`username`) REFERENCES users(`username`)
    FOREIGN KEY (`email`) REFERENCES users(`email`)
);
