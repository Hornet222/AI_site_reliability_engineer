from typing import  Optional
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
import logfire
from os import getenv
import asyncio
from dotenv import load_dotenv
import time
import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.models import SREInsight

# Load environment variables
load_dotenv()

# Configure logging
logfire.configure(token=getenv('LOGFIRE_TOKEN'))

# Initialize MCP servers
github_server = MCPServerStdio(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-github"],
    env={
        "GITHUB_PERSONAL_ACCESS_TOKEN": getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
    }
)

# Create SRE agent with ReAct pattern
sre_agent = Agent(
    model=getenv('LLM_MODEL', 'openai:gpt-4-turbo-preview'),
    mcp_servers=[github_server],
    instrument=True,
    result_type=SREInsight,
    system_prompt="""You are an AI Site Reliability Engineer assistant. Your task is to:
1. Monitor and analyze code changes in GitHub repositories
2. Assess security alerts and potential risks
3. Provide actionable insights and recommendations
4. Use the ReAct (Reason + Act) pattern to:
   - Analyze the current state
   - Decide on the next best action
   - Execute the action using available tools
   - Observe results and update understanding
   - Continue until you have sufficient information

Always maintain a security-first mindset and focus on reliability impact."""
)


async def generate_sre_insight(owner: str, repo: str) -> Optional[SREInsight]:
    """
    Generate SRE insights for a repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        
    Returns:
        SREInsight object or None if generation fails
    """
    try:
        async with sre_agent.run_mcp_servers():
            result = await sre_agent.run(
                user_prompt=f"""Analyze the GitHub repository {owner}/{repo} and generate insights about:
                1. Recent code changes and their impact
                2. Security vulnerabilities and risks
                3. Overall repository health
                
                Use the GitHub MCP server tools to gather data and provide actionable recommendations.
                Focus on:
                - Recent commits and their impact
                - Open security alerts
                - Code quality and maintainability
                - Potential risks and mitigation strategies"""
            )
            
            return result

    except Exception as e:
        logfire.error(f"Error in generate_sre_insight: {str(e)}", exc_info=True)
        return None

async def main():
    """Main entry point for the SRE agent."""
    try:
        # Example repository to analyze
        owner = getenv("GITHUB_OWNER", "Hornet222")
        repo = getenv("GITHUB_REPO", "pydantic-ai")

        print(f"\nAnalyzing repository: {owner}/{repo}")
        print("\nSRE Insight Report")
        print("=" * 50)
        
        result = await generate_sre_insight(owner, repo)
        
        if result and result.output:
            insight = result.output
            print(f"\nRepository: {insight.repository}\n")
            
            # Print Recent Code Changes
            print("Recent Code Changes:")
            for change in insight.code_changes:
                print(f"- Commit: {change.commit_sha[:8]}")
                print(f"  Author: {change.author}")
                print(f"  Impact Score: {change.impact_score}")
                print(f"  Message: {change.message}")
                if change.files_changed:
                    print(f"  Files Changed: {', '.join(change.files_changed)}")
                print()
            
            # Print Security Alerts
            print("Security Alerts:")
            if insight.security_alerts and len(insight.security_alerts) > 0:
                for alert in insight.security_alerts:
                    print("- Security Alert:")
                    if hasattr(alert, 'severity'):
                        print(f"  Severity: {alert.severity}")
                    if hasattr(alert, 'state'):
                        print(f"  State: {alert.state}")
                    if hasattr(alert, 'description'):
                        print(f"  Description: {alert.description}")
                    print()
            else:
                print("- No security alerts found\n")
            
            # Print Risk Assessment
            print("Risk Assessment:")
            print(insight.risk_assessment)
            print()
            
            # Print Recommendations
            print("Recommendations:")
            for rec in insight.recommendations:
                print(f"- {rec}")
            
        else:
            print("\nNo insight was generated. Check the logs for errors.")

    except Exception as e:
        print(f"\nError in main: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 