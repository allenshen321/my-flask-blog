# my-flask-blog
flask 搭建的博客,功能持续增加中

**2018-9-15 更新了用户角色功能**

包括:赋予角色与角色验证

**2018-9-17 增加了邮件确认功能**


####使用说明

1. 安装requirements中对应的环境

    pip install -r dev.txt
  
2. 本程序用的是mysql数据库，根据自己需要确保安装了相应的数据库。并建立了配置文件中相对应的数据库。

3. 迁移文件之后,需要手动添加角色
    
    python manage.py shell
    
    Role.insert_roles()
    
    if \_\_name__ == '\_\_main__' 