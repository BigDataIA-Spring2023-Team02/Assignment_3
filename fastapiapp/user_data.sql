CREATE TABLE if not exists user_data (
    username TEXT PRIMARY KEY,
    password TEXT,
    role TEXT CHECK(role IN ('admin','user')),
    plan TEXT CHECK(plan IN ('Free','Gold','Platinum')),
    register_time TEXT
);

DELETE FROM user_data;

INSERT INTO user_data VALUES('damg7245','$2b$12$yJ/iddK8UQjzx0oC3M/WteYutgmtGgub8uukDPZHj4gkk69hN97Jy','admin','platinum',DateTime('now'));
INSERT INTO user_data VALUES('user_free','$2b$12$E2h35wKPuFb3Vr8uC6Du8uzukmu0f2wM44uzm.UthGjKzKHEiMZNK','user','free',DateTime('now'));
INSERT INTO user_data VALUES('user_gold','$2b$12$l7JWANZU3dr3/sQXx18FBu.oH6LMBeJy9EKuF/YcK0nFQ3N6UbZx6','user','gold',DateTime('now'));
INSERT INTO user_data VALUES('user_platinum','$2b$12$reKZJlqbGQNOfEm8cWJpK.AkU8OxGoQcv6sJsos1A9fGiYzimXV9m','user','platinum',DateTime('now'));