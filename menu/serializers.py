from rest_framework import serializers
from .models import Menu_Object, Categories, Cart, Add_item_to_cart,Order , Orderd_Food
from users.serializers import UserSerializer

class simple_menu_serializer(serializers.ModelSerializer):
    class Meta:
        model = Menu_Object
        fields =['food_id', 'food_name', 'price','is_avilable']

class Menu_ObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu_Object
        fields = ['food_id', 'food_name', 'food_image', 'price', 'description', 'is_avilable']
        extra_kwarg = {'food_id':{'read_only': True}}

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation.pop('food_image')
    #     return representation
    

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'
        
class ViewCartItemserializer(serializers.ModelSerializer):
    sub_total = serializers.SerializerMethodField(method_name= 'total')

    food = Menu_ObjectSerializer(many =False)
 
    class Meta:
        model = Add_item_to_cart
        fields = ['add_to_cart_id','food', 'quantity', 'sub_total']

    def total(self, obj):
        return obj.quantity * obj.food.price
    

class AddToCartSerializer(serializers.ModelSerializer):
    sub_total = serializers.SerializerMethodField(method_name= 'total')

    food = simple_menu_serializer(many =False)
 
    class Meta:
        model = Add_item_to_cart
        fields = ['add_to_cart_id','food', 'quantity', 'sub_total']

    def total(self, obj):
        return obj.quantity * obj.food.price
    
class AddCartItemSerializer(serializers.ModelSerializer):
    food_id = serializers.UUIDField()
    
    def check_food(self , value):
        if not Menu_Object.objects.filter(pk = value).exists():
            raise serializers.ValidationError('there is no such product')
        return value
        
    
    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        food_id = self.validated_data['food_id']
        quantity = self.validated_data['quantity']
        
        try:
            item = Add_item_to_cart.objects.get(food_id = food_id , cart_id = cart_id)
            item.quantity += quantity
            item.save()
            self.instance = item
            
        except:
            self.instance = Add_item_to_cart.objects.create(food_id = food_id , cart_id = cart_id , quantity = quantity)
            
    class Meta:
        model = Add_item_to_cart
        fields = [ 'add_to_cart_id','food_id', 'quantity']
        
class Update_cart_serializer(serializers.ModelSerializer):
    class Meta:
        model = Add_item_to_cart
        fields = ['add_to_cart_id', 'quantity']
        extra_kwargs = {'add_to_cart_id':{'read_only': True}}
        


class Create_Cart_Serializer(serializers.ModelSerializer):
    cart_id = serializers.UUIDField(read_only = True)
    class Meta:
        model = Cart
        fields = ['cart_id']


class CartSerializer(serializers.ModelSerializer):
    cart_item = AddToCartSerializer(many=True)
    total = serializers.SerializerMethodField(method_name='total_price')
    cart_id = serializers.UUIDField()

    class Meta:
        model = Cart
        fields = ['cart_id', 'created_at', 'cart_item','total']
        extra_kwarg = {'created_at':{'read_only': True}}
        
    def total_price(self , cart : Cart):
        foods= cart.cart_item.all()
        price = sum([food.quantity * food.food.price for food in foods ])
        return price

    '''def create(self, validated_data):
        cart_items_data = validated_data.pop('items')
        cart = Cart.objects.create(user=self.context['request'].user, **validated_data)
        cart_items = []
        for item_data in cart_items_data:
            item = Add_item_to_cart.objects.create(cart=cart, **item_data)
            cart_items.append(item)
        cart.items.set(cart_items)
        return cart'''
        
# class OrderedFoodSerializer(serializers.ModelSerializer):
#     sub_total = serializers.SerializerMethodField(method_name= 'total')

#     food = Menu_ObjectSerializer(many =False)
 
#     class Meta:
#         model = Orderd_Food
#         fields = ['food', 'quantity', 'sub_total']

#     def total(self, obj):
#         return obj.quantity * obj.food.price
class OrderedFoodSerializer(serializers.ModelSerializer):
    sub_total = serializers.SerializerMethodField(method_name='total')

    food = Menu_ObjectSerializer(many=False)

    class Meta:
        model = Orderd_Food
        fields = ['food', 'quantity', 'sub_total']

    def total(self, obj):
        return obj.quantity * obj.food.price

    def create(self, validated_data):
        # Calculate and set sub_total before creating the Orderd_Food instance
        validated_data['sub_total'] = validated_data['quantity'] * validated_data['food'].price
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Calculate and set sub_total before updating the Orderd_Food instance
        validated_data['sub_total'] = validated_data['quantity'] * validated_data['food'].price
        return super().update(instance, validated_data)

    
class Order_Serializer(serializers.ModelSerializer):
    ordered_food = OrderedFoodSerializer(many = True)
    total = serializers.SerializerMethodField(method_name='total_price')
    # location = serializers.SerializerMethodField(method_name='get_location')
    user = UserSerializer()
    class Meta:
        model = Order
    
        fields = ['order_id','state','created_at','is_canceled','delivered_at','total','payment_mode','user','ordered_food','location']
        extra_kwarg = {'user':{'read_only': True}}

    def total_price(self, order: Order):
        foods = order.ordered_food.all()
        price = sum([food.quantity * food.food.price for food in foods])
        return price
    
    # def get_location(self, order: Order):
    #     user = order.user  # Access the user directly from the order
    #     profile = user.profile
    #     location = Location.objects.get(userProfile=profile)
    #     return location.name
        
        

class OrderIdSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    
