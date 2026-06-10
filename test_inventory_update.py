#!/usr/bin/env python3
"""
Test script to verify inventory updates are working properly.
Run this script in Odoo shell to test the inventory update functionality.
"""

def test_inventory_update():
    """Test function to verify inventory updates"""
    
    # Get a test purchase order in 'pending' state
    po = env['purchase.order'].search([('state', '=', 'pending')], limit=1)
    
    if not po:
        print("❌ No Purchase Orders found in 'pending' state")
        print("Please create a PO and set it to 'pending' state first")
        return False
    
    print(f"🔍 Testing PO: {po.name}")
    print(f"📊 Current state: {po.state}")
    
    # Check if PO has custom lines
    if hasattr(po, 'custom_line_ids') and po.custom_line_ids:
        print(f"📦 Found {len(po.custom_line_ids)} custom lines")
        for line in po.custom_line_ids:
            print(f"   - {line.name}: {line.quantity} {line.unit}")
    else:
        print("❌ No custom lines found in PO")
        return False
    
    # Check current stock before approval
    print("\n📊 Stock levels BEFORE approval:")
    for line in po.custom_line_ids:
        product = env['product.template'].search([('name', '=', line.name)], limit=1)
        if product:
            quant = env['stock.quant'].search([
                ('product_id', '=', product.product_variant_id.id),
                ('location_id.usage', '=', 'internal')
            ], limit=1)
            current_qty = quant.quantity if quant else 0
            print(f"   - {line.name}: {current_qty} units")
    
    # Test the approval process
    print(f"\n🚀 Approving PO: {po.name}")
    
    # Call action_confirm method
    try:
        po.action_confirm()
        print("✅ action_confirm() called successfully")
    except Exception as e:
        print(f"❌ Error calling action_confirm(): {e}")
        return False
    
    # Check state after approval
    po.refresh()
    print(f"📊 State after approval: {po.state}")
    
    # Check stock levels after approval
    print("\n📊 Stock levels AFTER approval:")
    for line in po.custom_line_ids:
        product = env['product.template'].search([('name', '=', line.name)], limit=1)
        if product:
            quant = env['stock.quant'].search([
                ('product_id', '=', product.product_variant_id.id),
                ('location_id.usage', '=', 'internal')
            ], limit=1)
            current_qty = quant.quantity if quant else 0
            print(f"   - {line.name}: {current_qty} units")
    
    # Check chatter messages
    print(f"\n💬 Recent chatter messages:")
    messages = po.message_ids[:5]  # Last 5 messages
    for msg in messages:
        if msg.body and ('Stock updated' in msg.body or 'DEBUG' in msg.body):
            print(f"   - {msg.body}")
    
    return True

# Run the test
if __name__ == "__main__":
    print("🧪 Testing Inventory Update Functionality")
    print("=" * 50)
    test_inventory_update()
