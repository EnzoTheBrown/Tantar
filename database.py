from peewee import PostgresqlDatabase

db = PostgresqlDatabase('tantar', user='tantar', password='tantar', host='postgres', port=5432)


class User(db.Model):
    username = db.CharField(unique=True)
    email = db.CharField(unique=True)
    hashed_password = db.CharField()


class Company(db.Model):
    name = db.CharField(unique=True)
    location = db.CharField()
    description = db.TextField()


class UserCompany(db.Model):
    user = db.ForeignKeyField(User)
    company = db.ForeignKeyField(Company)


class File(db.Model):
    name = db.CharField(unique=True)
    s3_path = db.CharField()


class CompanyFile(db.Model):
    company = db.ForeignKeyField(Company)
    file = db.ForeignKeyField(File)


class FileMetaData(db.Model):
    file = db.ForeignKeyField(File)
    key = db.CharField()
    value = db.CharField()
