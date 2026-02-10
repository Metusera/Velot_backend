import graphene
from .queries.user import UserQueries
from .queries.program import ProgramQueries
from .queries.testimonial import TestimonialQueries
from .mutations.auth import AuthMutations
from .mutations.user import UserMutations
from .mutations.program import ProgramMutations
from .mutations.testimonial import TestimonialMutations


class Query(
    UserQueries,
    ProgramQueries,
    TestimonialQueries,
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
    graphene.ObjectType
):
    """
    Root Mutation - combines all mutation classes.
    """
    pass


# Create the schema
schema = graphene.Schema(query=Query, mutation=Mutation)
