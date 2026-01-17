# ============================================================================
# 配置常量
# ============================================================================

IGNORE_DIRS = {
    'node_modules', '__pycache__', '.git', '.svn', '.hg',
    'dist', 'build', 'target', 'out', '.next', '.nuxt',
    'vendor', 'venv', '.venv', 'env', '.env',
    'coverage', '.nyc_output', '.pytest_cache',
    '.idea', '.vscode', '.vs', '.cursor',
    'Pods', 'DerivedData',
}

IGNORE_PATTERNS = {
    '*.min.js', '*.min.css', '*.map', '*.lock',
    '*.pyc', '*.pyo', '*.class', '*.o', '*.so',
    '.DS_Store', 'Thumbs.db',
}

CONFIG_FILES = {
    'package.json': 'Node.js',
    'pyproject.toml': 'Python',
    'setup.py': 'Python',
    'requirements.txt': 'Python',
    'Cargo.toml': 'Rust',
    'go.mod': 'Go',
    'pom.xml': 'Java (Maven)',
    'build.gradle': 'Java (Gradle)',
    'Gemfile': 'Ruby',
    'composer.json': 'PHP',
    'pubspec.yaml': 'Dart/Flutter',
    'Package.swift': 'Swift',
}

FRAMEWORK_PATTERNS = {
    'react': ['react', 'react-dom'],
    'vue': ['vue'],
    'angular': ['@angular/core'],
    'next.js': ['next'],
    'nuxt': ['nuxt'],
    'express': ['express'],
    'fastapi': ['fastapi'],
    'django': ['django'],
    'flask': ['flask'],
    'spring': ['spring-boot'],
    'rails': ['rails'],
    'laravel': ['laravel/framework'],
}

CODE_EXTENSIONS = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.c', '.cpp', '.h', '.cs', '.hpp', '.cxx', '.hxx', '.cc', '.hh'}

EXTENSION_TO_LANG = {
    '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
    '.jsx': 'JavaScript (React)', '.tsx': 'TypeScript (React)',
    '.java': 'Java', '.go': 'Go', '.rs': 'Rust',
    '.rb': 'Ruby', '.php': 'PHP', '.swift': 'Swift',
    '.kt': 'Kotlin', '.cs': 'C#', '.cpp': 'C++', '.c': 'C',
    '.hpp': 'C++', '.cxx': 'C++', '.hxx': 'C++', '.cc': 'C++', '.hh': 'C++',
}
