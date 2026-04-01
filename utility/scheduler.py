import time
import threading
from typing import List, Dict, Any
from datetime import datetime
from utility.logging_utility import logger
from utility.blogs import load_blogs, update_blog


def check_scheduled_blogs() -> None:
    try:
        blogs: List[Dict[str, Any]] = load_blogs()
        current_time: int = int(time.time())
        
        for blog in blogs:
            if blog.get("status") == "draft" and blog.get("scheduled_date"):
                try:
                    scheduled_time: int = int(blog.get("scheduled_date"))
                    
                    if scheduled_time <= current_time:
                        blog_id = blog.get("id")
                        logger.info(f'Publishing scheduled blog: "{blog.get("title")}" (ID: {blog_id})')
                        
                        if update_blog(blog_id, {"status": "visible"}):
                            logger.info(f'Successfully published blog: "{blog.get("title")}"')
                        else:
                            logger.error(f'Failed to publish blog: "{blog.get("title")}"')
                except (ValueError, TypeError) as e:
                    logger.error(f'Error processing scheduled blog {blog.get("id")}: {str(e)}')
    except Exception as e:
        logger.error(f"Error in blog scheduler: {str(e)}")


def start_scheduler() -> None:
    def scheduler_loop() -> None:
        logger.info("Blog scheduler started")
        while True:
            try:
                check_scheduled_blogs()
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
            time.sleep(60)
    
    thread = threading.Thread(target=scheduler_loop)
    thread.daemon = True
    thread.start()
    logger.debug("Blog scheduler thread started in background")
