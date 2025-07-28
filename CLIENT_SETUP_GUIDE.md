# 🔧 Client Setup Guide
## TunisieSMS Module Configuration

### 📋 Prerequisites

Before installing the TunisieSMS module, ensure you have:

1. **Odoo 13** installed and running
2. **TUNISIESMS Account** with API access
3. **Database Admin Access** to your Odoo instance
4. **Docker** (if using containerized setup)

---

### 🚀 Quick Installation

#### Step 1: Download & Install
```bash
# Download the module
git clone [your-repository-url]
cd odoo_SMS_Module

# Copy to Odoo addons directory
cp -r tunisiesms /path/to/your/odoo/addons/

# Restart Odoo server
sudo systemctl restart odoo
```

#### Step 2: Install Module
1. Open Odoo web interface
2. Go to **Apps** menu
3. Update Apps List
4. Search for "Tunisie SMS" 
5. Click **Install**

---

### ⚙️ Configuration Required

#### 1. SMS Gateway Setup
Navigate to: **Settings > Technical > SMS > Gateway**

Configure the following fields:
```
Name: TUNISIESMS (or your preferred name)
Gateway URL: https://api.l2t.io/tn/v0/api/api.aspx
Username: [YOUR_TUNISIESMS_USERNAME]
Password: [YOUR_TUNISIESMS_PASSWORD]
API Key: [YOUR_TUNISIESMS_API_KEY]
Sender ID: [YOUR_SENDER_ID]
```

#### 2. SMS Templates (Optional)
Navigate to: **SMS > Templates**

Customize these templates for your business:
- **Order Created Template**
- **Order Confirmed Template**  
- **Order Completed Template**
- **Order Cancelled Template**

**Template Variables:**
- `%name%` - Order number
- `%partner_id%` - Customer name
- `%amount_total%` - Order total
- `%date_order%` - Order date
- `%user_id%` - Salesperson

#### 3. Customer Mobile Numbers
Ensure customer records have mobile numbers in international format:
- ✅ Correct: `21612345678` (Tunisia)
- ✅ Correct: `33123456789` (France)
- ❌ Wrong: `+21612345678` (no + symbol)

---

### 🐳 Docker Setup (Recommended)

#### docker-compose.yml
```yaml
version: '3.8'
services:
  db:
    image: postgres:11
    environment:
      - POSTGRES_DB=your_database_name
      - POSTGRES_USER=your_db_user
      - POSTGRES_PASSWORD=your_db_password
    volumes:
      - odoo-db:/var/lib/postgresql/data
    ports:
      - "5433:5432"

  odoo:
    build: .
    depends_on:
      - db
    ports:
      - "8069:8069"
    environment:
      - HOST=db
      - USER=your_db_user
      - PASSWORD=your_db_password
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./addons:/mnt/extra-addons

volumes:
  odoo-web-data:
  odoo-db:
```

#### Start Services
```bash
# Build and start
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs odoo
```

---

### 🧪 Testing Setup

#### 1. Create Test Customer
Navigate to: **Contacts > Create**
```
Name: Test Customer
Mobile: 21612345678  # Use your test number
Email: test@yourcompany.com
```

#### 2. Test SMS Sending
1. Go to **Sales > Orders > Create**
2. Select your test customer
3. Add products and confirm order
4. Check **SMS > History** for sent messages

#### 3. Run Test Suite (Optional)
```bash
# Access container
docker exec -it your-odoo-container odoo shell -d your_database

# Run tests
exec(open('/tmp/test/basic_order_sms_test_fixed.py').read())
```

---

### 🔒 Security Configuration

#### 1. User Permissions
The module automatically grants SMS permissions to all users. To customize:

Navigate to: **Settings > Users & Companies > Users**
- Select user
- Go to **Technical Settings** tab
- Check **SMS Server Groups** permissions

#### 2. Access Control
For restricted access:
1. Create custom user groups
2. Assign specific users to SMS access
3. Configure gateway user permissions

---

### 📊 Monitoring & Maintenance

#### Check SMS Status
Navigate to: **SMS > Message Queue**
- **Draft**: Pending messages
- **Sent**: Successfully delivered
- **Error**: Failed messages (check error details)

#### View SMS History
Navigate to: **SMS > History**
- Complete audit trail of all SMS
- Delivery status and timestamps
- User who sent each message

#### Troubleshooting
Common issues and solutions:

1. **"No SMS Gateway found"**
   - Ensure gateway is properly configured
   - Check API credentials

2. **"Permission denied"**
   - Run: Settings > Technical > SMS > Refresh User Access
   - Check user permissions

3. **SMS not sending**
   - Verify customer mobile number format
   - Check SMS credits with provider
   - Review error logs

---

### 📞 Support

#### Documentation
- **Full Documentation**: See README.md
- **API Reference**: Included in README.md
- **Test Documentation**: See test/README.md

#### Issue Reporting
When reporting issues, include:
- Odoo version
- Module version
- Error messages
- Steps to reproduce

#### Contact
- **Technical Support**: [Your support contact]
- **Documentation**: [Your documentation URL]
- **Updates**: [Your repository URL]

---

### 🔄 Updates & Maintenance

#### Regular Maintenance
- Monitor SMS queue for stuck messages
- Archive old SMS history periodically
- Update SMS templates as needed
- Check SMS provider credits regularly

---

**✅ Your TunisieSMS module is now ready for production use!**

*For additional support or custom development, contact your module provider.*
