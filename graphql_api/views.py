from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from graphene_django.views import GraphQLView as BaseGraphQLView


@method_decorator(csrf_exempt, name='dispatch')
class GraphQLView(BaseGraphQLView):
    """
    Custom GraphQL view that:
    - Disables CSRF (auth is via JWT in the Authorization header)
    - Passes the Django request as the Graphene context so that
      info.context.user is available in all resolvers/decorators.
    """

    def get_context(self, request):
        return request
