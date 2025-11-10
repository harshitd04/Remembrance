"""
Summary generation service using LangChain and GPT-4o Mini.
"""
from typing import Dict, List
from datetime import datetime, timedelta
import logging
from langchain_openai import ChatOpenAI
from app.services.json_storage_service import JSONStorageService

logger = logging.getLogger(__name__)


class SummaryService:
    """Generate hierarchical summaries using LangChain."""
    
    def __init__(self, api_key: str, username: str = 'harshit'):
        """
        Initialize summary service.
        
        Args:
            api_key: OpenAI API key
            username: Username for user-specific data access
        """
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=api_key)
        self.storage = JSONStorageService(username=username)
    
    def generate_weekly_summary(self, week_num: int, year: int, force_regenerate: bool = False) -> Dict:
        """
        Generate weekly summary for a specific week.
        
        Args:
            week_num: ISO week number (1-52)
            year: Year
            force_regenerate: If True, regenerate even if cached summary exists
            
        Returns:
            Dictionary with summary data
        """
        try:
            period_id = f"{year}_{week_num}"
            
            # Check if summary already exists (unless force regenerate)
            if not force_regenerate:
                cached_summary = self.storage.load_summary('weekly', period_id)
                if cached_summary:
                    logger.info(f"Loaded cached weekly summary for week {week_num}, {year}")
                    cached_summary['cached'] = True
                    return cached_summary
            # Calculate date range for the week
            # ISO week starts on Monday
            jan_1 = datetime(year, 1, 1)
            week_start = jan_1 + timedelta(weeks=week_num - 1)
            week_start = week_start - timedelta(days=week_start.weekday())
            week_end = week_start + timedelta(days=6)
            
            # Load entries for the week
            all_entries = self.storage.load_all_entries()
            week_entries = []
            
            current_date = week_start
            while current_date <= week_end:
                date_str = current_date.strftime('%Y-%m-%d')
                if date_str in all_entries:
                    for entry in all_entries[date_str]:
                        week_entries.append({
                            'date': date_str,
                            'content': entry['content']
                        })
                current_date += timedelta(days=1)
            
            if not week_entries:
                title = f"Week {week_num} ({week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')})"
                return {
                    "week_number": week_num,
                    "year": year,
                    "title": title,
                    "start_date": week_start.strftime('%Y-%m-%d'),
                    "end_date": week_end.strftime('%Y-%m-%d'),
                    "date_range": f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}",
                    "summary": "## No Entries\n\nNo journal entries were recorded for this week.",
                    "entries_count": 0
                }
            
            # Combine entries
            combined_text = "\n---\n".join([
                f"Date: {e['date']}\n{e['content']}" for e in week_entries
            ])
            
            # Generate summary
            prompt = f"""Analyze this week's journal entries and create a well-structured summary.

Format your response EXACTLY like this:

## Key Emotions and Moods
[Describe the emotional landscape of the week]

## Major Accomplishments and Progress
[List key achievements and progress made]

## Challenges Faced
[Describe difficulties and obstacles encountered]

## Recurring Themes and Patterns
[Identify patterns and recurring topics]

## Personal Insights and Learnings
[Highlight key takeaways and lessons learned]

Journal entries:
{combined_text}"""
            
            response = self.llm.invoke(prompt)
            summary_text = response.content
            
            logger.info(f"Generated weekly summary for week {week_num}, {year}")
            
            # Format the title
            title = f"Week {week_num} ({week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')})"
            
            summary_data = {
                "week_number": week_num,
                "year": year,
                "title": title,
                "start_date": week_start.strftime('%Y-%m-%d'),
                "end_date": week_end.strftime('%Y-%m-%d'),
                "date_range": f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}",
                "summary": summary_text,
                "entries_count": len(week_entries),
                "generated_at": datetime.now().isoformat(),
                "cached": False
            }
            
            # Save summary to storage
            self.storage.save_summary('weekly', period_id, summary_data)
            
            return summary_data
            
        except Exception as e:
            logger.error(f"Weekly summary generation error: {str(e)}", exc_info=True)
            raise
    
    def generate_monthly_summary(self, month: int, year: int, force_regenerate: bool = False) -> Dict:
        """
        Generate monthly summary from weekly summaries.
        
        Args:
            month: Month number (1-12)
            year: Year
            force_regenerate: If True, regenerate even if cached summary exists
            
        Returns:
            Dictionary with summary data
        """
        try:
            period_id = f"{year}_{month}"
            
            # Check if summary already exists (unless force regenerate)
            if not force_regenerate:
                cached_summary = self.storage.load_summary('monthly', period_id)
                if cached_summary:
                    logger.info(f"Loaded cached monthly summary for {month}/{year}")
                    cached_summary['cached'] = True
                    return cached_summary
            # This is a simplified version
            # In production, you would load weekly summaries and combine them
            
            # Load all entries for the month
            all_entries = self.storage.load_all_entries()
            month_entries = []
            
            for date_str, entries in all_entries.items():
                date_obj = datetime.fromisoformat(date_str)
                if date_obj.year == year and date_obj.month == month:
                    for entry in entries:
                        month_entries.append(entry['content'])
            
            if not month_entries:
                month_name = datetime(year, month, 1).strftime('%B')
                title = f"{month_name} {year}"
                return {
                    "month": month,
                    "year": year,
                    "title": title,
                    "summary": "## No Entries\n\nNo journal entries were recorded for this month.",
                    "entries_count": 0
                }
            
            combined_text = "\n---\n".join(month_entries[:10])  # Limit for token usage
            
            prompt = f"""Analyze these journal entries and create a cohesive monthly overview.

Format your response EXACTLY like this:

## Overview
[Brief overview of the month]

## Major Developments
[Key events and developments]

## Personal Growth
[Areas of growth and self-improvement]

## Challenges and Solutions
[Problems faced and how they were addressed]

## Highlights
[Memorable moments and achievements]

## Looking Forward
[Insights and intentions for the next month]

Journal entries:
{combined_text}"""
            
            response = self.llm.invoke(prompt)
            
            logger.info(f"Generated monthly summary for {month}/{year}")
            
            month_name = datetime(year, month, 1).strftime('%B')
            title = f"{month_name} {year}"
            
            summary_data = {
                "month": month,
                "year": year,
                "title": title,
                "summary": response.content,
                "entries_count": len(month_entries),
                "generated_at": datetime.now().isoformat(),
                "cached": False
            }
            
            # Save summary to storage
            self.storage.save_summary('monthly', period_id, summary_data)
            
            return summary_data
            
        except Exception as e:
            logger.error(f"Monthly summary generation error: {str(e)}", exc_info=True)
            raise
    
    def generate_yearly_summary(self, year: int, force_regenerate: bool = False) -> Dict:
        """
        Generate yearly summary from monthly summaries.
        
        Args:
            year: Year
            force_regenerate: If True, regenerate even if cached summary exists
            
        Returns:
            Dictionary with summary data
        """
        try:
            period_id = str(year)
            
            # Check if summary already exists (unless force regenerate)
            if not force_regenerate:
                cached_summary = self.storage.load_summary('yearly', period_id)
                if cached_summary:
                    logger.info(f"Loaded cached yearly summary for {year}")
                    cached_summary['cached'] = True
                    return cached_summary
            # Load all entries for the year
            all_entries = self.storage.load_all_entries()
            year_entries = []
            
            for date_str, entries in all_entries.items():
                date_obj = datetime.fromisoformat(date_str)
                if date_obj.year == year:
                    for entry in entries:
                        year_entries.append(entry['content'])
            
            if not year_entries:
                title = f"Year in Review: {year}"
                return {
                    "year": year,
                    "title": title,
                    "summary": "## No Entries\n\nNo journal entries were recorded for this year.",
                    "entries_count": 0
                }
            
            # Sample entries for token efficiency
            combined_text = "\n---\n".join(year_entries[:20])
            
            prompt = f"""Synthesize these journal entries into a comprehensive annual review for {year}.

Format your response EXACTLY like this:

## Year in Review: {year}

### Life Trajectory
[Overall direction and evolution throughout the year]

### Major Milestones
[Significant achievements and life events]

### Personal Growth
[How you've grown and evolved]

### Challenges Overcome
[Difficulties faced and lessons learned]

### Relationships and Connections
[Important relationships and social developments]

### Professional/Academic Progress
[Career or educational achievements]

### Health and Wellness
[Physical and mental health journey]

### Key Learnings
[Most important insights and realizations]

### Looking Ahead
[Reflections and intentions for the future]

Journal entries from {year}:
{combined_text}"""
            
            response = self.llm.invoke(prompt)
            
            logger.info(f"Generated yearly summary for {year}")
            
            title = f"Year in Review: {year}"
            
            summary_data = {
                "year": year,
                "title": title,
                "summary": response.content,
                "entries_count": len(year_entries),
                "generated_at": datetime.now().isoformat(),
                "cached": False
            }
            
            # Save summary to storage
            self.storage.save_summary('yearly', period_id, summary_data)
            
            return summary_data
            
        except Exception as e:
            logger.error(f"Yearly summary generation error: {str(e)}", exc_info=True)
            raise
