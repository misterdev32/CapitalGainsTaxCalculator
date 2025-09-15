#!/usr/bin/env python3
"""
Script to create GitHub issues from the task breakdown
"""

import re
import subprocess
import sys
from pathlib import Path

def read_tasks_file():
    """Read the tasks.md file and parse tasks"""
    tasks_file = Path("specs/001-a-personalized-version/tasks.md")
    if not tasks_file.exists():
        print(f"Error: {tasks_file} not found")
        sys.exit(1)
    
    with open(tasks_file, 'r') as f:
        content = f.read()
    
    return content

def parse_tasks(content):
    """Parse tasks from markdown content"""
    tasks = []
    
    # Find all task lines with pattern: - [ ] T### [P?] Description
    task_pattern = r'- \[ \] (T\d+)\s*(\[P\])?\s*(.+)'
    
    for line in content.split('\n'):
        match = re.match(task_pattern, line)
        if match:
            task_id = match.group(1)
            is_parallel = bool(match.group(2))
            description = match.group(3).strip()
            
            # Extract phase from context
            phase = "Unknown"
            if "Phase 3.1: Setup" in content[:content.find(line)]:
                phase = "Setup"
            elif "Phase 3.2: Tests First" in content[:content.find(line)]:
                phase = "Tests (TDD)"
            elif "Phase 3.3: Core Implementation" in content[:content.find(line)]:
                phase = "Core Implementation"
            elif "Phase 3.4: Integration" in content[:content.find(line)]:
                phase = "Integration"
            elif "Phase 3.5: Polish" in content[:content.find(line)]:
                phase = "Polish"
            
            tasks.append({
                'id': task_id,
                'phase': phase,
                'is_parallel': is_parallel,
                'description': description
            })
    
    return tasks

def create_github_issue(task):
    """Create a GitHub issue for a task"""
    title = f"{task['id']}: {task['description']}"
    
    # Create issue body
    body = f"""## Task Details
- **Task ID**: {task['id']}
- **Phase**: {task['phase']}
- **Parallel**: {'Yes' if task['is_parallel'] else 'No'}

## Description
{task['description']}

## Acceptance Criteria
- [ ] Task completed according to specification
- [ ] Code follows project standards
- [ ] Tests pass (if applicable)
- [ ] Documentation updated (if applicable)

## Notes
This task was automatically created from the task breakdown in `specs/001-a-personalized-version/tasks.md`
"""
    
    # Create labels
    labels = [task['phase'].lower().replace(' ', '-'), 'task']
    if task['is_parallel']:
        labels.append('parallel')
    
    # Create the issue using gh CLI
    cmd = [
        'gh', 'issue', 'create',
        '--title', title,
        '--body', body,
        '--label', ','.join(labels)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Created issue for {task['id']}: {title}")
            return result.stdout.strip()
        else:
            print(f"❌ Failed to create issue for {task['id']}: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Error creating issue for {task['id']}: {e}")
        return None

def main():
    """Main function"""
    print("🚀 Creating GitHub issues from task breakdown...")
    
    # Read and parse tasks
    content = read_tasks_file()
    tasks = parse_tasks(content)
    
    print(f"📋 Found {len(tasks)} tasks to create issues for")
    
    # Create issues
    created_issues = []
    for task in tasks:
        issue_url = create_github_issue(task)
        if issue_url:
            created_issues.append(issue_url)
    
    print(f"\n🎉 Successfully created {len(created_issues)} issues!")
    print(f"📊 Total tasks: {len(tasks)}")
    print(f"✅ Created: {len(created_issues)}")
    print(f"❌ Failed: {len(tasks) - len(created_issues)}")
    
    if created_issues:
        print(f"\n🔗 View issues at: https://github.com/misterdev32/CapitalGainsTaxCalculator/issues")

if __name__ == "__main__":
    main()
