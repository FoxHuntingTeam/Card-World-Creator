from sqlalchemy import create_engine, Column, Integer, String, Boolean, Sequence, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, Mapped, mapped_column, Session

DATABASE_URL = 'sqlite:///database.db'
Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False)


class Cards(Base):
    __tablename__ = 'cards'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    respect: Mapped[int] = mapped_column(nullable=True)
    type: Mapped[str] = mapped_column(default="alpha")
    rarity_id: Mapped[int] = mapped_column()
    full: Mapped[bool] = mapped_column(default=False)
    project: Mapped[str] = mapped_column(nullable=True)

class Projects(Base):
    __tablename__ = 'projects'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=True)
    type: Mapped[str] = mapped_column(default="VC")
    folder: Mapped[str] = mapped_column()

class ThisProject(Base):
    __tablename__ = 'this_project'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=True)

class Frames(Base):
    __tablename__ = 'frames'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    folder: Mapped[str] = mapped_column(nullable=True)
    type: Mapped[str] = mapped_column()
    respect: Mapped[int] = mapped_column()
    project: Mapped[str] = mapped_column()
    x_num: Mapped[int] = mapped_column(default=0)
    y_num: Mapped[int] = mapped_column(default=0)
    x_text: Mapped[int] = mapped_column(default=0)
    y_text: Mapped[int] = mapped_column(default=0)
    font_num: Mapped[str] = mapped_column(nullable=True)
    font_text: Mapped[str] = mapped_column(nullable=True)
    embossing_text: Mapped[bool] = mapped_column(default=False)
    shadow_text: Mapped[bool] = mapped_column(default=False)
    embossing_num: Mapped[bool] = mapped_column(default=False)
    shadow_num: Mapped[bool] = mapped_column(default=False)
    element_mumber: Mapped[bool] = mapped_column(default=True)
    font_num_size: Mapped[int] = mapped_column(default=8)
    font_text_size: Mapped[int] = mapped_column(default=8)
    color_text: Mapped[str] = mapped_column(default="white")
    color_num: Mapped[str] = mapped_column(default="white")

Base.metadata.create_all(engine)

#Base.metadata.drop_all(bind=engine, tables=[User.__table__])
#Base.metadata.drop_all(bind=engine, tables=[Clan.__table__])
#Base.metadata.drop_all(bind=engine, tables=[UserRespect.__table__])
#Base.metadata.drop_all(bind=engine, tables=[ClanRespect.__table__])
#Base.metadata.drop_all(bind=engine, tables=[Inventory.__table__])
#Base.metadata.drop_all(bind=engine, tables=[Cards.__table__])
#Base.metadata.drop_all(bind=engine, tables=[Mythical.__table__])
#Base.metadata.drop_all(bind=engine, tables=[Quests.__table__])
#sBase.metadata.drop_all(bind=engine, tables=[Traids.__table__])

def add_to_base(data):
    with Session(engine) as session:
        with session.begin():
            session.add(data)