# Logic And Stories - Deployment Guide

## Render Deployment with PostgreSQL Database

This guide walks you through deploying the Logic And Stories website to Render with a PostgreSQL database.

### Prerequisites

1. **GitHub Repository**: Your code should be in https://github.com/bricks4tricks/LogicAndStories/
2. **Render Account**: Sign up at https://render.com
3. **Render MCP Integration**: Already configured with your token

### Step 1: Prepare Your Repository

Ensure these files are in your repository root:

```
logic-stories-website/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── models.py             # Database models
├── migrate_database.py   # Database initialization
├── requirements.txt      # Python dependencies
├── render.yaml           # Render deployment config
├── .env.example         # Environment variables template
├── templates/           # HTML templates
├── static/             # CSS, JS, images
└── README.md           # Documentation
```

### Step 2: Deploy to Render

#### Option A: Using Render Dashboard

1. **Connect Repository**:
   - Go to https://dashboard.render.com
   - Click "New +"
   - Select "Blueprint"
   - Connect your GitHub account
   - Select `bricks4tricks/LogicAndStories` repository
   - Choose the branch containing your code

2. **Configure Services**:
   - Render will automatically detect the `render.yaml` file
   - Review the configuration:
     - Web Service: `logic-stories-website`
     - Database: `logic-stories-db` (PostgreSQL)
   - Click "Apply"

#### Option B: Using Render MCP (Already Connected)

Since you have Render MCP configured, you can also deploy using the MCP commands:

```bash
# In your terminal with MCP configured
/mcp render deploy --service-name logic-stories-website
```

### Step 3: Environment Variables

Render will automatically set these environment variables from `render.yaml`:

- `FLASK_ENV`: production
- `SECRET_KEY`: Auto-generated secure key
- `DATABASE_URL`: PostgreSQL connection string from database service

### Step 4: Database Setup

The database will be automatically initialized during deployment:

1. **Database Creation**: Render creates PostgreSQL database
2. **Schema Setup**: `migrate_database.py` runs during build
3. **Sample Data**: Sample stories are added automatically

### Step 5: Verify Deployment

1. **Check Build Logs**:
   - Monitor the build process in Render dashboard
   - Look for successful database migration messages

2. **Test the Application**:
   - Visit your deployed URL (e.g., `https://logic-stories-website.onrender.com`)
   - Test user registration and login
   - Browse the story library
   - Try the interactive story player

### Step 6: Domain Configuration (Optional)

1. **Custom Domain**:
   - In Render dashboard, go to your service settings
   - Add your custom domain
   - Update DNS settings as instructed

### Database Schema

The application creates these tables automatically:

```sql
-- Users table
users (id, email, username, password_hash, first_name, last_name, user_type, grade_level, ...)

-- Stories table  
stories (id, story_id, title, description, grade_level, math_strand, fl_best_standards, ...)

-- User progress tracking
user_progress (id, user_id, story_id, completion_percentage, correct_answers, ...)

-- Classroom management
classrooms (id, teacher_id, name, grade_level, join_code, ...)
classroom_students (classroom_id, student_id)

-- Assignments
assignments (id, teacher_id, student_id, story_id, due_date, ...)
```

### Key Features Available

After deployment, these features will be live:

#### ✅ **Authentication System**
- User registration (Student/Parent/Teacher)
- Secure login/logout
- Role-based access control
- Password hashing with bcrypt

#### ✅ **Story Library**
- 12+ sample stories across K-12
- Florida B.E.S.T. standards alignment
- Grade-level filtering
- Interactive story player

#### ✅ **Progress Tracking**
- Individual student dashboards
- Completion percentages
- Standards mastery tracking
- Time spent analytics

#### ✅ **Database Integration**
- PostgreSQL database
- User accounts and progress persistence
- Story content management
- Scalable data model

### Monitoring and Maintenance

1. **Logs**: Monitor application logs in Render dashboard
2. **Database**: Use Render's database tools for maintenance
3. **Performance**: Monitor resource usage and scaling needs
4. **Updates**: Push to GitHub to trigger automatic redeployments

### Troubleshooting

#### Common Issues:

1. **Build Failures**:
   ```bash
   # Check Python dependencies
   pip install -r requirements.txt
   
   # Test database connection locally
   python migrate_database.py
   ```

2. **Database Connection Issues**:
   - Verify `DATABASE_URL` environment variable
   - Check PostgreSQL service status in Render
   - Review database logs

3. **Authentication Problems**:
   - Ensure `SECRET_KEY` is set
   - Check Flask session configuration
   - Verify user creation in database

#### Debug Mode:

To enable debug mode temporarily:
```bash
# In Render dashboard, add environment variable:
FLASK_DEBUG=True
```

**⚠️ Remember to disable debug mode in production!**

### Production Considerations

1. **Security**:
   - SECRET_KEY is auto-generated and secure
   - Database credentials are managed by Render
   - HTTPS is enabled by default

2. **Performance**:
   - Free tier limitations: 512MB RAM, sleeps after 15min inactivity
   - Consider upgrading for production workloads
   - Database connection pooling is configured

3. **Scaling**:
   - Horizontal scaling available on paid plans
   - Database can be upgraded independently
   - CDN integration for static assets

### Next Steps

1. **Content Creation**: Add more stories and curriculum content
2. **User Testing**: Gather feedback from students and teachers
3. **Feature Enhancement**: Add requested features based on usage
4. **Performance Optimization**: Monitor and optimize based on traffic

### Support

- **Render Documentation**: https://render.com/docs
- **Flask Documentation**: https://flask.palletsprojects.com/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/

---

**Deployment Status**: ✅ Ready for production deployment
**Database**: ✅ PostgreSQL configured
**Authentication**: ✅ Full user management system
**Content**: ✅ Sample curriculum data loaded