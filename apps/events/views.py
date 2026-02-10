from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.events.models import Testimonial


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_testimonial_image(request):
    """
    REST endpoint for uploading testimonial images.
    Requires authentication and superuser permission.
    """
    if not request.user.is_superuser:
        return Response({'error': 'Superuser permission required'}, status=status.HTTP_403_FORBIDDEN)

    testimonial_id = request.data.get('testimonial_id')
    image = request.FILES.get('image')

    if not testimonial_id or not image:
        return Response({'error': 'testimonial_id and image are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        testimonial = Testimonial.objects.get(id=testimonial_id)
        testimonial.image = image
        testimonial.save()
        return Response({'message': 'Image uploaded successfully'}, status=status.HTTP_200_OK)
    except Testimonial.DoesNotExist:
        return Response({'error': 'Testimonial not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)