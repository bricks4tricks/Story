# Logic And Stories - Sample Website

A sample website for Logic And Stories, demonstrating a K-12 math education platform that teaches mathematics through engaging stories aligned with Florida B.E.S.T. standards.

## Features

- **Complete K-12 Coverage**: Content spanning from Kindergarten through 12th grade
- **Florida B.E.S.T. Alignment**: 642 mathematics standards covered across all grade levels
- **Age-Appropriate Design**: Interface and content complexity adapts to each grade level
- **Interactive Stories**: Sample math adventures with embedded problem-solving
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Story Library**: Organized by grade level and mathematical strands

## Technology Stack

- **Backend**: Python 3 with Flask
- **Frontend**: HTML5, CSS3 (Tailwind CSS), JavaScript
- **Deployment**: Configured for Render hosting
- **Database**: In-memory data structures (expandable to PostgreSQL/MongoDB)

## Grade Level Structure

### Elementary (K-2): Ages 4-7
- 75 Florida B.E.S.T. Standards
- 5-10 minute story duration
- Large buttons and simple navigation
- Audio narration support

### Primary (3-5): Ages 8-10
- 109 Florida B.E.S.T. Standards
- 10-20 minute story duration
- Interactive problem-solving
- Progress tracking

### Middle School (6-8): Ages 11-13
- 114 Florida B.E.S.T. Standards
- 15-30 minute story duration
- Advanced mathematical concepts
- Social features

### High School (9-12): Ages 14-18
- 337 Florida B.E.S.T. Standards
- 20-45 minute story duration
- Complex mathematical modeling
- Real-world applications

## Mathematical Strands Covered

- **Number Sense and Operations**: 108 standards
- **Algebraic Reasoning**: 148 standards
- **Geometric Reasoning**: 103 standards
- **Data Analysis and Probability**: 81 standards
- **Fractions**: 21 standards
- **Measurement**: 23 standards
- **Functions**: 26 standards
- **Calculus**: 45 standards
- **Trigonometry**: 23 standards
- **Financial Literacy**: 27 standards
- **Logic and Discrete Theory**: 30 standards

## Sample Stories Included

1. **"Counting Creatures in the Enchanted Forest"** (Kindergarten)
   - Standard: MA.K.NSO.1.1
   - Interactive counting adventure with forest animals

2. **"Coordinate Grid Treasure Hunt"** (Grade 5)
   - Standard: MA.5.GR.3.1
   - Navigate coordinate grids to find pirate treasure

3. **"Financial Freedom Quest"** (High School)
   - Standard: MA.912.FL.3.3
   - Learn credit and debt management through real scenarios

## Installation & Setup

### Local Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd logic-stories-website
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Visit**: `http://localhost:5000`

### Render Deployment

This application is configured for easy deployment on Render:

1. Push code to GitHub repository
2. Connect repository to Render
3. Use the included `render.yaml` configuration
4. Deploy automatically

## File Structure

```
logic-stories-website/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment config
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Homepage
│   ├── stories.html      # Story library
│   ├── story_detail.html # Individual story player
│   ├── for_parents.html  # Parent information page
│   ├── for_teachers.html # Teacher resources page
│   └── about.html        # About page
├── static/               # Static assets
│   ├── css/
│   │   └── styles.css    # Custom CSS styles
│   ├── js/               # JavaScript files
│   └── images/           # Image assets
└── data/                 # Data files
```

## Key Features Demonstrated

### 1. Standards-Aligned Content
- Every story mapped to specific Florida B.E.S.T. benchmarks
- Complete coverage of 642 K-12 mathematics standards
- Progress tracking by standard mastery

### 2. Age-Appropriate Design
- **K-2**: Large buttons, simple interface, audio support
- **3-5**: Medium complexity, visual progress indicators
- **6-8**: Standard interface with social features
- **9-12**: Advanced tools and collaboration features

### 3. Interactive Story Player
- Multi-step story progression
- Embedded mathematical problems
- Immediate feedback and hints
- Progress tracking and completion rewards

### 4. Teacher & Parent Dashboards
- Class management tools
- Standards coverage reports
- Individual student progress
- Assignment and assessment features

### 5. Responsive Design
- Mobile-first approach
- Tablet and desktop optimization
- Accessibility features
- High contrast and reduced motion support

## Educational Approach

### Narrative-Based Learning
Stories create emotional connections that enhance memory and understanding of mathematical concepts.

### Standards Alignment
Precise mapping to Florida B.E.S.T. standards ensures curriculum compliance while maintaining engagement.

### Differentiated Instruction
Content complexity and interface design adapt to developmental stages and learning needs.

### Assessment Integration
Formative assessment embedded naturally within story experiences.

## API Endpoints

- `GET /`: Homepage
- `GET /stories`: Story library with filtering
- `GET /story/<story_id>`: Individual story detail and player
- `GET /for-parents`: Parent information and pricing
- `GET /for-teachers`: Teacher resources and classroom tools
- `GET /about`: About page with mission and approach
- `GET /api/stories/<grade_level>`: JSON API for grade-specific stories

## Customization

### Adding New Stories
1. Update `CURRICULUM_DATA` in `app.py`
2. Add story content to story player JavaScript
3. Create corresponding templates if needed

### Modifying Grade Levels
1. Update curriculum data structure
2. Modify filtering logic in JavaScript
3. Adjust CSS classes for age-appropriate styling

### Extending Features
- Add user authentication
- Implement database storage
- Create admin interface
- Add payment processing
- Integrate with school systems

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance Considerations

- Optimized images and assets
- Efficient CSS using Tailwind
- Minimal JavaScript dependencies
- CDN-delivered external resources
- Responsive image loading

## Future Enhancements

1. **User Management**: Complete authentication and user profiles
2. **Progress Persistence**: Database storage for user progress
3. **Advanced Analytics**: Detailed learning analytics dashboard
4. **Content Management**: Admin interface for story creation
5. **Mobile App**: Native mobile applications
6. **Gamification**: Enhanced reward systems and achievements
7. **Collaboration**: Student-to-student and teacher collaboration tools
8. **Accessibility**: Enhanced accessibility features and testing
9. **Multilingual**: Support for multiple languages
10. **Integration**: LMS and gradebook integrations

## License

This is a sample/demonstration website. For actual licensing terms, contact Logic And Stories.

## Contact

For questions about this sample implementation:
- Email: info@logicandstories.com
- Phone: (555) 123-4567

---

*This sample website demonstrates the potential of story-based mathematics education aligned with educational standards.*