from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, CheckConstraint, TIMESTAMP, Index
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.functions import current_timestamp

Base = declarative_base()

# task priorities for look-up table
PRIORITY_LEVELS = ["Lowest", "Low", "Medium", "High", "Highest"]
MIN_PRIORITY = 0
MAX_PRIORITY = len(PRIORITY_LEVELS) - 1

# task statuses for look-up table
STATUSES = ["Open", "In Progress", "Resolved", "Closed", "Reopened"]
MIN_STATUS = 0
MAX_STATUS = len(STATUSES) - 1


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    hash = Column(String, nullable=False)

    tasks_assigned = relationship('Task', foreign_keys='Task.assigner_id')
    tasks_assigned_to = relationship('Task', foreign_keys='Task.assignee_id')
    user_comment = relationship('Comment', foreign_keys='Comment.user_id')
    user_notification = relationship('Notification', foreign_keys='Notification.user_id')

    username_index = Index('username_index', username)


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String)
    timestamp = Column(TIMESTAMP, nullable=False, default=current_timestamp())
    due_date = Column(Date, nullable=False)
    assigner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    assignee_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    priority_id = Column(Integer, ForeignKey('priorities.id'), nullable=False, default=MIN_PRIORITY)
    status_id = Column(Integer, ForeignKey('statuses.id'), nullable=False, default=MIN_STATUS)
    
    task_comment = relationship('Comment', foreign_keys='Comment.task_id')
    task_notification = relationship('Notification', foreign_keys='Notification.task_id')

    __table_args__ = (
        CheckConstraint(f'priority_id BETWEEN {MIN_PRIORITY} AND {MAX_PRIORITY}', name='priority_check'),
        CheckConstraint(f'status_id BETWEEN {MIN_STATUS} AND {MAX_STATUS}', name='status_check')
    )

    assignee_id_index = Index('assignee_id_index', assignee_id)
    assigner_id_index = Index('assigner_id_index', assigner_id)
    status_id_index = Index('status_id_index', status_id)


class Priority(Base):
    """Look-up table"""
    __tablename__ = 'priorities'

    id = Column(Integer, primary_key=True)
    level = Column(String, nullable=False, unique=True)

    task_with_priority = relationship('Task', foreign_keys='Task.priority_id')


class Status(Base):
    """Look-up table"""
    __tablename__ = 'statuses'

    id = Column(Integer, primary_key=True)
    status = Column(String, nullable=False, unique=True)

    task_with_status = relationship('Task', foreign_keys='Task.status_id')


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False, default=current_timestamp())

    
class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False, default=current_timestamp())


def create_db():
    """create the database"""

    # Establish a database connection
    database_url = 'sqlite:///tasks.db'

    # Create an engine to connect to a SQLite database
    engine = create_engine(database_url)

    # Create the tables in the database
    Base.metadata.create_all(engine)

    with sessionmaker(bind=engine)() as sql_session:
        for id, level in enumerate(PRIORITY_LEVELS):
            new_priority = Priority(id=id, level=level)
            sql_session.add(new_priority)

        for id, status in enumerate(STATUSES):
            new_status = Status(id=id, status=status)
            sql_session.add(new_status)

        sql_session.commit()


if __name__ == "__main__":
    create_db()
