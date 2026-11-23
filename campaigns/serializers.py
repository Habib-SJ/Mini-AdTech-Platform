from rest_framework import serializers


class CTRResponseSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField()
    campaign_title = serializers.CharField(max_length=100)
    ctr = serializers.FloatField(allow_null=True)



class ReportQuerySerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError({
                "start_date": "start_date must not be after end_date"
            })
        return data    


class CampaignReportSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    
    impressions = serializers.IntegerField()
    clicks = serializers.IntegerField()
    
    cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    ctr = serializers.FloatField(allow_null=True)
