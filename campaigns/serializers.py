from rest_framework import serializers


class CTRResponseSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField()
    campaign_title = serializers.CharField(max_length=100)
    ctr = serializers.FloatField(allow_null=True)