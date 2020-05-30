from rest_framework import serializers
from .models import Articles2,Tickets,PaymentSettlement,TicketDiscounts


class EditViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articles2
        fields = '__all__'

class EditTicketSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tickets
        fields = '__all__'

class PaymentSettlementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentSettlement
        fields = '__all__'

class TicketDiscountsSerializer(serializers.ModelSerializer):
	class Meta:
		model = TicketDiscounts
		fields = '__all__'
