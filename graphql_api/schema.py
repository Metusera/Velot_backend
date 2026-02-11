import graphene
from .queries.user import UserQueries
from .queries.program import ProgramQueries
from .queries.testimonial import TestimonialQueries
from .queries.invitation import InvitationQueries
from .queries.enrollment import EnrollmentQueries
from .mutations.auth import AuthMutations
from .mutations.user import UserMutations
from .mutations.program import ProgramMutations
from .mutations.testimonial import TestimonialMutations
from .mutations.invitation import InvitationMutations
from .mutations.enrollment import EnrollmentMutations


class Query(
    UserQueries,
    ProgramQueries,
    TestimonialQueries,
    InvitationQueries,
    EnrollmentQueries,
    graphene.ObjectType
):
    """
    Root Query - combines all query classes.
    """
    pass


class Mutation(
    AuthMutations,
    UserMutations,
    ProgramMutations,
    TestimonialMutations,
    InvitationMutations,
    EnrollmentMutations,
    graphene.ObjectType
):
    """
    Root Mutation - combines all mutation classes.
    """
    pass


# Create the schema
schema = graphene.Schema(query=Query, mutation=Mutation)
