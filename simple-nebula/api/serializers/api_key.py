from rest_framework import serializers
from ..models import APIKey, Node, Lighthouse
from .base import BaseModelSerializer


class APIKeySerializer(BaseModelSerializer):
    key = serializers.CharField(write_only=True, required=False)
    node_id = serializers.UUIDField(write_only=True, required=False)
    lighthouse_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = APIKey
        fields = (
            'id', 'name', 'key', 'entity_type',
            'node_id', 'lighthouse_id', 'expires_at',
            'last_used', 'is_active', 'created_at'
        )
        read_only_fields = ('id', 'key_hash', 'last_used', 'created_at')

    def validate(self, attrs):
        node_id = attrs.pop('node_id', None)
        lighthouse_id = attrs.pop('lighthouse_id', None)
        entity_type = attrs.get('entity_type')

        if not node_id and not lighthouse_id:
            raise serializers.ValidationError(
                'Either node_id or lighthouse_id must be provided'
            )

        if node_id and lighthouse_id:
            raise serializers.ValidationError(
                'Cannot specify both node_id and lighthouse_id'
            )

        if node_id:
            if entity_type != APIKey.EntityTypes.NODE:
                raise serializers.ValidationError(
                    'Entity type must be "node" when specifying node_id'
                )
            try:
                attrs['node'] = Node.objects.get(id=node_id)
            except Node.DoesNotExist:
                raise serializers.ValidationError('Node not found')

        if lighthouse_id:
            if entity_type != APIKey.EntityTypes.LIGHTHOUSE:
                raise serializers.ValidationError(
                    'Entity type must be "lighthouse" when specifying lighthouse_id'
                )
            try:
                attrs['lighthouse'] = Lighthouse.objects.get(id=lighthouse_id)
            except Lighthouse.DoesNotExist:
                raise serializers.ValidationError('Lighthouse not found')

        return attrs 