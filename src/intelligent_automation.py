# -*- coding: utf-8 -*-
"""
Intelligent Automation System for NeuraSynth Project Management
Provides automated workflows, smart notifications, and predictive analytics
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .models import db, AutomationRule, SmartNotification, Project

class AutomationTrigger(Enum):
    """Types of automation triggers"""
    TIME_BASED = "time_based"
    EVENT_BASED = "event_based"
    CONDITION_BASED = "condition_based"
    MILESTONE_BASED = "milestone_based"
    BUDGET_BASED = "budget_based"
    DEADLINE_BASED = "deadline_based"

class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IntelligentAutomationEngine:
    """
    Core engine for intelligent automation and workflow management
    """
    
    def __init__(self, db):
        self.db = db
        self.automation_rules: Dict[str, AutomationRule] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self.load_rules()

    def load_rules(self):
        """Load automation rules from the database."""
        try:
            rules = AutomationRule.query.all()
            self.automation_rules = {rule.id: rule for rule in rules}
            self.logger.info(f"Loaded {len(self.automation_rules)} automation rules.")
        except Exception as e:
            self.logger.error(f"Error loading automation rules: {str(e)}")

    def add_automation_rule(self, rule_data: Dict[str, Any]) -> bool:
        """Add a new automation rule to the database"""
        try:
            rule = AutomationRule(**rule_data)
            self.db.session.add(rule)
            self.db.session.commit()
            self.automation_rules[rule.id] = rule
            self.logger.info(f"Added automation rule: {rule.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding automation rule: {str(e)}")
            return False
    
    def remove_automation_rule(self, rule_id: str) -> bool:
        """Remove an automation rule"""
        try:
            rule = AutomationRule.query.get(rule_id)
            if rule:
                self.db.session.delete(rule)
                self.db.session.commit()
                del self.automation_rules[rule_id]
                self.logger.info(f"Removed automation rule: {rule_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error removing automation rule from DB: {str(e)}")
            return False
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def trigger_event(self, event_type: str, event_data: Dict[str, Any]):
        """Trigger an event and execute associated handlers"""
        try:
            # Execute registered handlers
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    try:
                        await handler(event_data)
                    except Exception as e:
                        self.logger.error(f"Error in event handler: {str(e)}")
            
            # Check automation rules
            await self._check_event_based_rules(event_type, event_data)
            
        except Exception as e:
            self.logger.error(f"Error triggering event {event_type}: {str(e)}")
    
    async def _check_event_based_rules(self, event_type: str, event_data: Dict[str, Any]):
        """Check and execute event-based automation rules"""
        for rule in self.automation_rules.values():
            if not rule.is_active or rule.trigger_type != AutomationTrigger.EVENT_BASED:
                continue
            
            try:
                if self._evaluate_conditions(rule.conditions, event_data):
                    await self._execute_rule_actions(rule, event_data)
                    rule.last_executed = datetime.now()
                    rule.execution_count += 1
            except Exception as e:
                self.logger.error(f"Error executing rule {rule.name}: {str(e)}")
    
    def _evaluate_conditions(self, conditions: Dict[str, Any], context_data: Dict[str, Any]) -> bool:
        """Evaluate rule conditions against context data"""
        try:
            for condition_key, condition_value in conditions.items():
                if condition_key not in context_data:
                    return False
                
                if isinstance(condition_value, dict):
                    # Handle complex conditions (operators)
                    operator = condition_value.get('operator', 'equals')
                    expected_value = condition_value.get('value')
                    actual_value = context_data[condition_key]
                    
                    if operator == 'equals' and actual_value != expected_value:
                        return False
                    elif operator == 'greater_than' and actual_value <= expected_value:
                        return False
                    elif operator == 'less_than' and actual_value >= expected_value:
                        return False
                    elif operator == 'contains' and expected_value not in str(actual_value):
                        return False
                    elif operator == 'in' and actual_value not in expected_value:
                        return False
                else:
                    # Simple equality check
                    if context_data[condition_key] != condition_value:
                        return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error evaluating conditions: {str(e)}")
            return False
    
    async def _execute_rule_actions(self, rule: AutomationRule, context_data: Dict[str, Any]):
        """Execute actions for a triggered rule"""
        for action in rule.actions:
            try:
                action_type = action.get('type')
                
                if action_type == 'send_notification':
                    await self._send_notification_action(action, context_data)
                elif action_type == 'update_project_status':
                    await self._update_project_status_action(action, context_data)
                elif action_type == 'assign_task':
                    await self._assign_task_action(action, context_data)
                elif action_type == 'send_email':
                    await self._send_email_action(action, context_data)
                elif action_type == 'create_milestone':
                    await self._create_milestone_action(action, context_data)
                elif action_type == 'budget_alert':
                    await self._budget_alert_action(action, context_data)
                elif action_type == 'escalate_issue':
                    await self._escalate_issue_action(action, context_data)
                else:
                    self.logger.warning(f"Unknown action type: {action_type}")
                    
            except Exception as e:
                self.logger.error(f"Error executing action {action.get('type')}: {str(e)}")
    
    async def _send_notification_action(self, action: Dict[str, Any], context_data: Dict[str, Any]):
        """Send a smart notification"""
        try:
            notification = SmartNotification(
                recipient_id=action.get('recipient_id', context_data.get('user_id')),
                title=action.get('title', '').format(**context_data),
                message=action.get('message', '').format(**context_data),
                priority=NotificationPriority(action.get('priority', 'medium')),
                notification_type=action.get('notification_type', 'general'),
                data=context_data
            )
            self.db.session.add(notification)
            self.db.session.commit()
            self.logger.info(f"Queued notification in DB: {notification.title}")
        except Exception as e:
            self.logger.error(f"Error queuing notification in DB: {str(e)}")
    
    async def _update_project_status_action(self, action: Dict[str, Any], context_data: Dict[str, Any]):
        """Update project status"""
        project_id = action.get('project_id', context_data.get('project_id'))
        new_status = action.get('status', '').format(**context_data)
        
        # This would integrate with the project management system
        self.logger.info(f"Would update project {project_id} status to {new_status}")
    
    async def _assign_task_action(self, action: Dict[str, Any], context_data: Dict[str, Any]):
        """Assign a task automatically"""
        task_data = {
            'title': action.get('task_title', '').format(**context_data),
            'description': action.get('task_description', '').format(**context_data),
            'assignee_id': action.get('assignee_id', context_data.get('user_id')),
            'project_id': action.get('project_id', context_data.get('project_id')),
            'due_date': action.get('due_date'),
            'priority': action.get('priority', 'medium')
        }
        
        # This would integrate with the task management system
        self.logger.info(f"Would create task: {task_data['title']}")
    
    async def _send_email_action(self, action: Dict[str, Any], context_data: Dict[str, Any]):
        """Send an email notification"""
        email_data = {
            'to': action.get('to', '').format(**context_data),
            'subject': action.get('subject', '').format(**context_data),
            'body': action.get('body', '').format(**context_data)
        }
        
        # This would integrate with an email service
        self.logger.info(f"Would send email to {email_data['to']}: {email_data['subject']}")
    
    async def _create_milestone_action(self, action: Dict[str, Any], context_data: Dict[str, Any]):
        """Create a project milestone"""
        milestone_data = {
            'title': action.get('title', '').format(**context_data),
            'description': action.get('description', '').format(**context_data),
            'project_id': action.get('project_id', context_data.get('project_id')),
            'due_date': action.get('due_date'),
            'completion_criteria': action.get('completion_criteria', [])
        }
        
        # This would integrate with the project management system
        self.logger.info(f"Would create milestone: {milestone_data['title']}")
    
    async def _budget_alert_action(self, action: Dict[str, Any], context_data: Dict[str, Any]):
        """Send budget alert"""
        alert_data = {
            'project_id': context_data.get('project_id'),
            'current_spend': context_data.get('current_spend', 0),
            'budget_limit': context_data.get('budget_limit', 0),
            'threshold_percentage': action.get('threshold_percentage', 80)
        }
        
        # Calculate budget utilization
        utilization = (alert_data['current_spend'] / alert_data['budget_limit']) * 100 if alert_data['budget_limit'] > 0 else 0
        
        if utilization >= alert_data['threshold_percentage']:
            try:
                notification = SmartNotification(
                    recipient_id=action.get('recipient_id', context_data.get('project_manager_id')),
                    title=f"Budget Alert: Project {alert_data['project_id']}",
                    message=f"Project has used {utilization:.1f}% of budget ({alert_data['current_spend']}/{alert_data['budget_limit']})",
                    priority=NotificationPriority.HIGH,
                    notification_type='budget_alert',
                    data=alert_data
                )
                self.db.session.add(notification)
            except Exception as e:
                self.logger.error(f"Error creating budget alert notification: {str(e)}")
    
    async def _escalate_issue_action(self, action: Dict[str, Any], context_data: Dict[str, Any]):
        """Escalate an issue to higher management"""
        escalation_data = {
            'issue_id': context_data.get('issue_id'),
            'project_id': context_data.get('project_id'),
            'escalation_level': action.get('escalation_level', 1),
            'escalation_reason': action.get('reason', '').format(**context_data)
        }
        
        # This would integrate with the issue tracking system
        self.logger.info(f"Would escalate issue {escalation_data['issue_id']} to level {escalation_data['escalation_level']}")
    
    async def start_automation_engine(self):
        """Start the automation engine"""
        self.is_running = True
        self.logger.info("Automation engine started")
        
        while self.is_running:
            try:
                # Check time-based rules
                await self._check_time_based_rules()
                
                # Check condition-based rules
                await self._check_condition_based_rules()
                
                # Process notification queue
                # Notification processing is now handled by a separate worker/service
                
                # Sleep for a short interval
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in automation engine loop: {str(e)}")
                await asyncio.sleep(60)
    
    async def _check_time_based_rules(self):
        """Check and execute time-based automation rules"""
        current_time = datetime.now()
        
        for rule in self.automation_rules.values():
            if not rule.is_active or rule.trigger_type != AutomationTrigger.TIME_BASED:
                continue
            
            try:
                schedule = rule.conditions.get('schedule', {})
                
                # Check if it's time to execute
                if self._should_execute_time_based_rule(rule, current_time, schedule):
                    await self._execute_rule_actions(rule, {'current_time': current_time})
                    rule.last_executed = current_time
                    rule.execution_count += 1
                    
            except Exception as e:
                self.logger.error(f"Error checking time-based rule {rule.name}: {str(e)}")
    
    def _should_execute_time_based_rule(self, rule: AutomationRule, current_time: datetime, schedule: Dict[str, Any]) -> bool:
        """Determine if a time-based rule should be executed"""
        try:
            interval_minutes = schedule.get('interval_minutes')
            specific_time = schedule.get('specific_time')
            days_of_week = schedule.get('days_of_week', [])
            
            # Check day of week constraint
            if days_of_week and current_time.weekday() not in days_of_week:
                return False
            
            # Check specific time
            if specific_time:
                target_time = datetime.strptime(specific_time, '%H:%M').time()
                if current_time.time().hour != target_time.hour or current_time.time().minute != target_time.minute:
                    return False
            
            # Check interval
            if interval_minutes and rule.last_executed:
                time_since_last = current_time - rule.last_executed
                if time_since_last.total_seconds() < interval_minutes * 60:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error evaluating time-based rule: {str(e)}")
            return False
    
    async def _check_condition_based_rules(self):
        """Check condition-based rules against current system state"""
        # This would query the current system state and check conditions
        # For now, we'll skip this as it requires integration with the data layer
        pass
    
    async def _deliver_notification(self, notification: SmartNotification):
        """Deliver a notification to the recipient"""
        # This would integrate with various notification channels
        # (email, SMS, push notifications, in-app notifications)
        self.logger.info(f"Delivered notification to {notification.recipient_id}: {notification.title}")
    
    def stop_automation_engine(self):
        """Stop the automation engine"""
        self.is_running = False
        self.logger.info("Automation engine stopped")
    
    def get_automation_statistics(self) -> Dict[str, Any]:
        """Get statistics about automation rules and executions"""
        total_rules = len(self.automation_rules)
        active_rules = sum(1 for rule in self.automation_rules.values() if rule.is_active)
        total_executions = sum(rule.execution_count for rule in self.automation_rules.values())
        
        rule_types = {}
        for rule in self.automation_rules.values():
            rule_type = rule.trigger_type
            if rule_type not in rule_types:
                rule_types[rule_type] = 0
            rule_types[rule_type] += 1
        
        return {
            'total_rules': total_rules,
            'active_rules': active_rules,
            'total_executions': total_executions,
            'pending_notifications': SmartNotification.query.filter_by(is_read=False).count(),
            'rule_types': rule_types,
            'engine_status': 'running' if self.is_running else 'stopped'
        }


class ProjectHealthMonitor:
    """
    Monitor project health and trigger automated interventions
    """
    
    def __init__(self, db, automation_engine: IntelligentAutomationEngine):
        self.db = db
        self.automation_engine = automation_engine
        self.logger = logging.getLogger(__name__)
        
    def analyze_project_health(self, project: Project) -> Dict[str, Any]:
        """Analyze the health of a project"""
        health_score = 0
        issues = []
        recommendations = []
        
        # Budget health
        budget_used = project.budget_used or 0
        total_budget = project.total_budget or 1
        budget_utilization = budget_used / total_budget if total_budget > 0 else 0
        
        if budget_utilization > 0.9:
            issues.append("Budget nearly exhausted")
            health_score -= 20
        elif budget_utilization > 0.8:
            issues.append("Budget usage high.")
            health_score -= 10
        else:
            health_score += 10
        
        # Timeline health
        current_date = datetime.now()
        start_date = project.start_date or current_date
        end_date = project.end_date or current_date
        
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)

        total_duration = (end_date - start_date).days if end_date > start_date else 1
        elapsed_duration = (current_date - start_date).days
        progress_percentage = project.progress_percentage or 0
        
        if total_duration > 0:
            expected_progress = (elapsed_duration / total_duration) * 100
            progress_variance = progress_percentage - expected_progress
            
            if progress_variance < -20:
                issues.append("Project significantly behind schedule")
                health_score -= 25
            elif progress_variance < -10:
                issues.append("Project behind schedule")
                health_score -= 15
            else:
                health_score += 15
        
        # Team health
        team_size = project.team_size or 0
        active_members = project.active_members or 0
        
        if team_size > 0:
            team_utilization = active_members / team_size
            if team_utilization < 0.7:
                issues.append("Low team engagement")
                health_score -= 15
            else:
                health_score += 10
        
        # Quality metrics
        bug_count = project.open_bugs or 0
        if bug_count > 10:
            issues.append("High number of open bugs")
            health_score -= 10
        
        # Normalize health score
        health_score = max(0, min(100, health_score + 50))  # Base score of 50
        project.health_score = health_score
        project.health_status = self._get_health_status(health_score)
        self.db.session.commit()
        
        # Generate recommendations
        if budget_utilization > 0.8:
            recommendations.append("Review budget allocation and consider cost optimization")
        
        if progress_percentage < expected_progress:
            recommendations.append("Consider adding resources or adjusting timeline")
        
        if team_utilization < 0.8:
            recommendations.append("Improve team engagement and communication")
        
        return {
            'health_score': health_score,
            'health_status': self._get_health_status(health_score),
            'issues': issues,
            'recommendations': recommendations,
            'metrics': {
                'budget_utilization': budget_utilization,
                'progress_variance': progress_variance if 'progress_variance' in locals() else 0,
                'team_utilization': team_utilization if 'team_utilization' in locals() else 0
            }
        }
    
    def _get_health_status(self, health_score: float) -> str:
        """Get health status based on score"""
        if health_score >= 80:
            return "excellent"
        elif health_score >= 60:
            return "good"
        elif health_score >= 40:
            return "fair"
        elif health_score >= 20:
            return "poor"
        else:
            return "critical"
    
    async def monitor_project(self, project_id: str):
        """Monitor a project and trigger automated responses"""
        project = Project.query.get(project_id)
        if not project:
            self.logger.error(f"Project with ID {project_id} not found.")
            return

        health_analysis = self.analyze_project_health(project)
        
        # Trigger events based on health status
        if health_analysis['health_status'] in ['poor', 'critical']:
            await self.automation_engine.trigger_event('project_health_critical', {
                'project_id': project_id,
                'health_score': health_analysis['health_score'],
                'issues': health_analysis['issues'],
                'recommendations': health_analysis['recommendations']
            })
        
        # Trigger specific issue events
        for issue in health_analysis['issues']:
            if 'budget' in issue.lower():
                await self.automation_engine.trigger_event('budget_issue', {
                    'project_id': project_id,
                    'issue': issue,
                    'budget_utilization': health_analysis['metrics']['budget_utilization']
                })
            elif 'schedule' in issue.lower():
                await self.automation_engine.trigger_event('schedule_issue', {
                    'project_id': project_id,
                    'issue': issue,
                    'progress_variance': health_analysis['metrics']['progress_variance']
                })
        
        return health_analysis
