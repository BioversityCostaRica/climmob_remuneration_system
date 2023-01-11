# from climmob.models.meta import Base
# from climmob.models import Enumerator
#
# from sqlalchemy.orm import relationship
# from sqlalchemy import (
#     Column,
#     Index,
#     INTEGER,
#     Unicode,
#     ForeignKeyConstraint,
#     text,
# )
#
# from sqlalchemy.dialects.mysql import MEDIUMTEXT
#
#
# class EnumeratorRemunerationDetails(Base):
#     __tablename__ = "remuneration_enumerator_details"
#
#     __table_args__ = (
#         ForeignKeyConstraint(
#             ["supervisor_user", "supervisor_id"],
#             ["enumerator.user_name", "enumerator.enum_id"],
#             ondelete="SET NULL",
#         ),
#         ForeignKeyConstraint(
#             ["user_name", "enum_id"],
#             ["enumerator.user_name", "enumerator.enum_id"],
#             ondelete="CASCADE",
#         ),
#         Index(
#             "fk_remuneration_enumerator_details_supervisor_idx",
#             "supervisor_user",
#             "supervisor_id",
#         ),
#         Index(
#             "fk_remuneration_enumerator_details_enumerator_idx", "user_name", "enum_id"
#         ),
#     )
#
#     user_name = Column(Unicode(80), primary_key=True, nullable=False)
#     enum_id = Column(Unicode(80), primary_key=True, nullable=False)
#     is_supervisor = Column(INTEGER, server_default=text("'0'"))
#     supervisor_user = Column(Unicode(80))
#     supervisor_id = Column(Unicode(80))
#
#     enumerator = relationship(
#         "Enumerator",
#         primaryjoin="EnumeratorRemunerationDetails.supervisor_user == Enumerator.user_name",
#     )
