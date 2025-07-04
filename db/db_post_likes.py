import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from fastapi import HTTPException, status
from sqlalchemy.orm.session import Session 
from db.models import DbPost, DbPostLike
from sqlalchemy import func

def like_post(db: Session, post_id: int, user_id: int):
    post = db.query(DbPost).filter(DbPost.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id '{post_id}' not found"
        )

    if post.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="U mag niet uw eigen post liken!"
        )

    existing_like = db.query(DbPostLike).filter(
        DbPostLike.post_id == post_id,
        DbPostLike.user_id == user_id
    ).first()

    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="U heeft deze post al geliked."
        )

    new_like = DbPostLike(
        post_id=post_id,
        user_id=user_id
    )

    db.add(new_like)
    db.commit()
    db.refresh(new_like)
    return new_like

def unlike_post(db: Session, post_id: int, user_id: int):
    existing_like = db.query(DbPostLike).filter(
        DbPostLike.post_id == post_id,
        DbPostLike.user_id == user_id
    ).first()

    if not existing_like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="U heeft deze post niet geliked."
        )

    db.delete(existing_like)
    db.commit()
    return {"message": "Post succesvol unliked."}

def get_post_with_likes(db: Session, post_id: int, current_user_id: int):
    post = db.query(DbPost).filter(DbPost.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    liked_count = db.query(func.count(DbPostLike.id)).filter(
        DbPostLike.post_id == post_id
    ).scalar()

    has_liked = db.query(DbPostLike).filter(
        DbPostLike.post_id == post_id,
        DbPostLike.user_id == current_user_id
    ).first() is not None

    # # ✅ Logging zichtbaar maken in terminal
    # logger.info(f"LIKED COUNT: {liked_count}, HAS LIKED: {has_liked}")
    # print(f">>>> DEBUG: LIKED COUNT = {liked_count}, HAS LIKED = {has_liked}")


    return {
        "post": post,
        "liked_count": liked_count,
        "has_liked": has_liked
    }

