#!/usr/bin/env python3
"""
Standalone multiprocessing worker module
Fixes serialization issues by keeping worker function at module level
"""

from epic_enhanced_generator_fixed import EpicImageGeneratorFixed

def worker_process(args):
    """Standalone worker function for multiprocessing"""
    process_id, num_tasks = args
    try:
        # Create generator instance within the process
        generator = EpicImageGeneratorFixed()
        results = []
        for i in range(num_tasks):
            prompt = f"Process {process_id} epic scene {i} with divine characters"
            result = generator.enhance_prompt_epic_style(prompt)
            results.append(len(result))
        return (process_id, len(results), sum(results))
    except Exception as e:
        return (process_id, "ERROR", str(e))