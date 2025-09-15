#!/usr/bin/env python3
"""
Script to update documentation after task completion
This script should be run after each task is completed to update the wiki documentation
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def get_task_info():
    """Get current task information from GitHub issues"""
    try:
        # Get all open issues
        result = subprocess.run([
            'gh', 'issue', 'list', '--state', 'all', '--json', 'number,title,state,labels'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error getting issues: {result.stderr}")
            return None
        
        issues = json.loads(result.stdout)
        return issues
    except Exception as e:
        print(f"Error getting task info: {e}")
        return None

def update_task_progress():
    """Update the task progress documentation"""
    issues = get_task_info()
    if not issues:
        return False
    
    # Count tasks by phase
    phases = {
        'Setup': {'total': 6, 'completed': 0, 'in_progress': 0},
        'Tests': {'total': 15, 'completed': 0, 'in_progress': 0},
        'Core': {'total': 20, 'completed': 0, 'in_progress': 0},
        'Integration': {'total': 12, 'completed': 0, 'in_progress': 0},
        'Polish': {'total': 12, 'completed': 0, 'in_progress': 0}
    }
    
    # Count completed and in-progress tasks
    for issue in issues:
        title = issue['title']
        state = issue['state']
        labels = [label['name'] for label in issue.get('labels', [])]
        
        # Extract task ID and phase
        if title.startswith('T'):
            task_id = title.split(':')[0]
            task_num = int(task_id[1:])
            
            # Determine phase based on task number
            if 1 <= task_num <= 6:
                phase = 'Setup'
            elif 7 <= task_num <= 21:
                phase = 'Tests'
            elif 22 <= task_num <= 41:
                phase = 'Core'
            elif 42 <= task_num <= 53:
                phase = 'Integration'
            elif 54 <= task_num <= 65:
                phase = 'Polish'
            else:
                continue
            
            if state == 'CLOSED':
                phases[phase]['completed'] += 1
            elif 'in-progress' in labels:
                phases[phase]['in_progress'] += 1
    
    # Update the task progress file
    progress_file = Path('docs/wiki/Task-Progress.md')
    if not progress_file.exists():
        print(f"Progress file not found: {progress_file}")
        return False
    
    # Read current content
    with open(progress_file, 'r') as f:
        content = f.read()
    
    # Update progress summary table
    new_table = """## Progress Summary

| Phase | Total | Completed | In Progress | Remaining |
|-------|-------|-----------|-------------|-----------|"""
    
    total_completed = 0
    total_in_progress = 0
    total_remaining = 0
    
    for phase, stats in phases.items():
        remaining = stats['total'] - stats['completed'] - stats['in_progress']
        total_completed += stats['completed']
        total_in_progress += stats['in_progress']
        total_remaining += remaining
        
        new_table += f"\n| {phase} | {stats['total']} | {stats['completed']} | {stats['in_progress']} | {remaining} |"
    
    new_table += f"\n| **Total** | **65** | **{total_completed}** | **{total_in_progress}** | **{total_remaining}** |"
    
    # Replace the table in the content
    import re
    table_pattern = r'## Progress Summary.*?\| \*\*Total\*\*.*?\n'
    content = re.sub(table_pattern, new_table + '\n\n', content, flags=re.DOTALL)
    
    # Update last updated timestamp
    content = re.sub(
        r'\*Last updated: \d{4}-\d{2}-\d{2}\*',
        f'*Last updated: {datetime.now().strftime("%Y-%m-%d")}*',
        content
    )
    
    # Write updated content
    with open(progress_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated task progress: {total_completed} completed, {total_in_progress} in progress, {total_remaining} remaining")
    return True

def update_home_page():
    """Update the home page with current project status"""
    issues = get_task_info()
    if not issues:
        return False
    
    # Count completed tasks
    completed = sum(1 for issue in issues if issue['state'] == 'CLOSED')
    in_progress = sum(1 for issue in issues if 'in-progress' in [label['name'] for label in issue.get('labels', [])])
    remaining = 65 - completed - in_progress
    
    # Update home page
    home_file = Path('docs/wiki/Home.md')
    if not home_file.exists():
        return False
    
    with open(home_file, 'r') as f:
        content = f.read()
    
    # Update project status
    content = re.sub(
        r'- \*\*Total Tasks\*\*: \d+',
        f'- **Total Tasks**: 65',
        content
    )
    content = re.sub(
        r'- \*\*Completed\*\*: \d+',
        f'- **Completed**: {completed}',
        content
    )
    content = re.sub(
        r'- \*\*In Progress\*\*: \d+',
        f'- **In Progress**: {in_progress}',
        content
    )
    content = re.sub(
        r'- \*\*Remaining\*\*: \d+',
        f'- **Remaining**: {remaining}',
        content
    )
    
    # Update last updated timestamp
    content = re.sub(
        r'\*Last updated: \d{4}-\d{2}-\d{2}\*',
        f'*Last updated: {datetime.now().strftime("%Y-%m-%d")}*',
        content
    )
    
    with open(home_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated home page: {completed} completed, {in_progress} in progress, {remaining} remaining")
    return True

def create_task_completion_doc(task_id, task_title, completion_notes=""):
    """Create documentation for a completed task"""
    doc_file = Path(f'docs/wiki/tasks/T{task_id:03d}-{task_title.lower().replace(" ", "-").replace(":", "")}.md')
    doc_file.parent.mkdir(parents=True, exist_ok=True)
    
    content = f"""# Task T{task_id:03d}: {task_title}

**Completed**: {datetime.now().strftime("%Y-%m-%d")}
**Status**: ✅ Completed

## Description
{task_title}

## Implementation Details
{completion_notes}

## Files Modified
- List of files that were created or modified

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Documentation Updated
- [ ] Code comments added
- [ ] API documentation updated
- [ ] User guide updated (if applicable)

## Next Steps
- Related tasks that can now be started
- Dependencies resolved

---

*This task was automatically documented on {datetime.now().strftime("%Y-%m-%d")}*
"""
    
    with open(doc_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Created task completion documentation: {doc_file}")
    return True

def main():
    """Main function to update all documentation"""
    print("🚀 Updating documentation...")
    
    # Update task progress
    if update_task_progress():
        print("✅ Task progress updated")
    else:
        print("❌ Failed to update task progress")
    
    # Update home page
    if update_home_page():
        print("✅ Home page updated")
    else:
        print("❌ Failed to update home page")
    
    # If a specific task was completed, create its documentation
    if len(sys.argv) > 1:
        task_id = int(sys.argv[1])
        task_title = sys.argv[2] if len(sys.argv) > 2 else f"Task T{task_id:03d}"
        completion_notes = sys.argv[3] if len(sys.argv) > 3 else ""
        
        create_task_completion_doc(task_id, task_title, completion_notes)
    
    print("\n🎉 Documentation update complete!")
    print("📝 Remember to commit and push the updated documentation")

if __name__ == "__main__":
    main()
