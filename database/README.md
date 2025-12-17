# Database Configuration

This directory contains database-related configuration and setup files for the AI Interview Avatar System.

## MongoDB Setup

### Option 1: Local MongoDB Installation

1. **Install MongoDB Community Edition**
   - [Download MongoDB Community Server](https://www.mongodb.com/try/download/community)
   - Follow installation instructions for your operating system

2. **Start MongoDB Service**
   ```bash
   # Windows
   net start MongoDB
   
   # macOS/Linux
   sudo systemctl start mongod
   ```

3. **Verify Connection**
   ```bash
   mongosh
   # or
   mongo
   ```

### Option 2: MongoDB Atlas (Recommended for Development)

1. **Create Free Account**
   - Visit [MongoDB Atlas](https://www.mongodb.com/atlas)
   - Sign up for a free account

2. **Create Cluster**
   - Choose "Free" tier (M0)
   - Select cloud provider and region
   - Click "Create Cluster"

3. **Configure Network Access**
   - Go to Network Access
   - Add IP Address: `0.0.0.0/0` (for development)
   - Or add your specific IP address

4. **Create Database User**
   - Go to Database Access
   - Create a new user with read/write permissions
   - Remember username and password

5. **Get Connection String**
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your user password

## Environment Configuration

Update your `.env` file with the MongoDB connection:

```env
# For local MongoDB
MONGODB_URL=mongodb://localhost:27017

# For MongoDB Atlas
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/ai_interview_system?retryWrites=true&w=majority

DATABASE_NAME=ai_interview_system
```

## Database Collections

The system automatically creates the following collections:

- **users**: User accounts and authentication
- **interviews**: Interview configurations
- **candidates**: Candidate profiles
- **sessions**: Interview session instances
- **responses**: Candidate responses and files

## Indexes

The following indexes are automatically created for performance:

- `users.email` (unique)
- `interviews.interview_id` (unique)
- `candidates.email` (unique)
- `sessions.session_id` (unique)

## Data Backup

### Local MongoDB
```bash
# Create backup
mongodump --db ai_interview_system --out ./backup

# Restore backup
mongorestore --db ai_interview_system ./backup/ai_interview_system
```

### MongoDB Atlas
- Use Atlas built-in backup features
- Configure automated backups in cluster settings
- Manual exports available in cluster view

## Monitoring

### Local MongoDB
```bash
# Check database status
mongosh --eval "db.stats()"

# Check collection sizes
mongosh --eval "db.getSiblingDB('ai_interview_system').runCommand({collStats: 'users'})"
```

### MongoDB Atlas
- Built-in monitoring dashboard
- Performance metrics and alerts
- Query performance analysis

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure MongoDB service is running
   - Check if port 27017 is available
   - Verify firewall settings

2. **Authentication Failed**
   - Check username/password in connection string
   - Verify user has correct permissions
   - Ensure database name is correct

3. **Network Timeout**
   - Check internet connection
   - Verify IP whitelist in Atlas
   - Check network firewall settings

### Performance Tips

1. **Indexes**: Ensure all query fields are indexed
2. **Connection Pooling**: Use connection pooling for production
3. **Monitoring**: Set up alerts for slow queries
4. **Backup**: Regular automated backups
5. **Updates**: Keep MongoDB version updated

## Security Best Practices

1. **Network Security**
   - Use VPN for production deployments
   - Restrict IP access in Atlas
   - Enable TLS/SSL encryption

2. **Authentication**
   - Use strong passwords
   - Implement role-based access
   - Regular password rotation

3. **Data Protection**
   - Encrypt sensitive data
   - Regular security audits
   - Compliance with data regulations

## Development vs Production

### Development
- Local MongoDB or Atlas free tier
- Basic authentication
- Minimal security restrictions

### Production
- MongoDB Atlas paid tier or dedicated server
- Advanced security features
- Automated backups and monitoring
- Performance optimization
- Compliance and audit logging



