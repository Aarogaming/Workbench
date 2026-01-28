#!/usr/bin/env python3
"""PM-001: Convert Bot Execution Loops to Async/Await"""

import asyncio
from typing import Callable, Any, List, Dict


class AsyncExecutor:
    """Async bot execution executor"""

    def __init__(self):
        """Initialize async executor"""
        self.tasks: List[asyncio.Task] = []
        self.results: Dict[str, Any] = {}

    async def execute_task(self, task_id: str,
                           task_func: Callable) -> Any:
        """Execute single async task"""
        try:
            result = await task_func()
            self.results[task_id] = {'success': True, 'result': result}
            return result
        except Exception as e:
            self.results[task_id] = {'success': False, 'error': str(e)}
            return None

    async def execute_parallel(self, tasks: Dict[str, Callable]) -> Dict:
        """Execute multiple tasks in parallel"""
        coroutines = [
            self.execute_task(task_id, task_func)
            for task_id, task_func in tasks.items()
        ]

        await asyncio.gather(*coroutines)
        return self.results

    async def execute_sequence(self,
                               tasks: List[Callable]) -> List[Any]:
        """Execute tasks sequentially"""
        results = []
        for task in tasks:
            result = await task()
            results.append(result)
        return results

    def get_results(self) -> Dict[str, Any]:
        """Get execution results"""
        return self.results


class BotExecutionLoop:
    """Bot execution loop with async support"""

    def __init__(self, max_iterations: int = 100):
        """Initialize execution loop"""
        self.max_iterations = max_iterations
        self.executor = AsyncExecutor()
        self.iteration = 0

    async def run_loop(self, work_func: Callable) -> Dict[str, Any]:
        """Run async execution loop"""
        while self.iteration < self.max_iterations:
            try:
                await work_func()
                self.iteration += 1
            except Exception as e:
                return {
                    'completed': False,
                    'iterations': self.iteration,
                    'error': str(e)
                }

        return {
            'completed': True,
            'iterations': self.iteration,
            'status': 'finished'
        }

    async def run_with_timeout(self, work_func: Callable,
                               timeout: float) -> Dict[str, Any]:
        """Run with timeout"""
        try:
            result = await asyncio.wait_for(
                self.run_loop(work_func),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            return {
                'completed': False,
                'iterations': self.iteration,
                'error': 'Timeout exceeded'
            }

    def execute(self, work_func: Callable) -> Dict[str, Any]:
        """Execute loop (non-async wrapper)"""
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(self.run_loop(work_func))
            return result
        finally:
            loop.close()


class AsyncBotManager:
    """Manages async bot execution"""

    def __init__(self):
        """Initialize bot manager"""
        self.bots: Dict[str, BotExecutionLoop] = {}
        self.execution_stats: Dict[str, Dict] = {}

    def create_bot(self, bot_id: str,
                   max_iterations: int = 100) -> BotExecutionLoop:
        """Create new async bot"""
        bot = BotExecutionLoop(max_iterations)
        self.bots[bot_id] = bot
        return bot

    async def execute_bot(self, bot_id: str,
                          work_func: Callable) -> Dict[str, Any]:
        """Execute specific bot"""
        bot = self.bots.get(bot_id)
        if not bot:
            return {'error': 'Bot not found'}

        result = await bot.run_loop(work_func)
        self.execution_stats[bot_id] = result
        return result

    async def execute_all(self, work_func: Callable) -> Dict[str, Any]:
        """Execute all bots"""
        tasks = {
            bot_id: bot.run_loop(work_func)
            for bot_id, bot in self.bots.items()
        }

        results = await asyncio.gather(
            *[asyncio.create_task(task) for task in tasks.values()]
        )

        return {
            'total_bots': len(self.bots),
            'completed': len(results),
            'results': results
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return {
            'total_bots': len(self.bots),
            'executions': len(self.execution_stats),
            'stats': self.execution_stats
        }
