from typing import List

from fastapi import APIRouter, HTTPException, Cookie

from anonymous_board.adapter.input.web.request.create_anonymous_board_request import (
    CreateAnonymousBoardRequest,
)
from anonymous_board.adapter.input.web.response.anonymous_board_response import (
    AnonymousBoardResponse,
)
from anonymous_board.application.usecase.anonymous_board_usecase import (
    AnonymousBoardUseCase,
)

from account.application.usecase.account_usecase import AccountUseCase
from config.helpers.auth_session import get_google_sub_from_session  # 세션 → sub 함수 (이미 있는 걸 가정)


anonymous_board_router = APIRouter(tags=["board"])

usecase = AnonymousBoardUseCase.getInstance()
account_usecase = AccountUseCase.getInstance()

@anonymous_board_router.post("/create", response_model=AnonymousBoardResponse)
def create_board(
    request: CreateAnonymousBoardRequest,
    session_id: str | None = Cookie(None),
):
    google_sub = get_google_sub_from_session(session_id)
    if not google_sub:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")

    my_account = account_usecase.get_my_account(google_sub)
    writer_nickname = (
        my_account.nickname if my_account and my_account.nickname else None
    )

    board = usecase.create_board(
        request.title,
        request.content,
        writer_sub=google_sub,
        writer_nickname=writer_nickname,
    )

    return AnonymousBoardResponse(
        id=board.id,
        title=board.title,
        content=board.content,
        writer_nickname=board.writer_nickname,
        created_at=board.created_at,
        updated_at=board.updated_at,
    )


@anonymous_board_router.get("/list", response_model=List[AnonymousBoardResponse])
def list_boards():
    boards = usecase.list_boards()
    return [
        AnonymousBoardResponse(
            id=b.id,
            title=b.title,
            content=b.content,
            writer_nickname=b.writer_nickname,
            created_at=b.created_at,
            updated_at=b.updated_at,
        )
        for b in boards
    ]


@anonymous_board_router.get("/read/{board_id}", response_model=AnonymousBoardResponse)
def get_board(board_id: int):
    board = usecase.get_board(board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return AnonymousBoardResponse(
        id=board.id,
        title=board.title,
        content=board.content,
        writer_nickname=board.writer_nickname,
        created_at=board.created_at,
        updated_at=board.updated_at,
    )


@anonymous_board_router.delete("/delete/{board_id}")
def delete_board(board_id: int):
    success = usecase.delete_board(board_id)
    if not success:
        raise HTTPException(status_code=404, detail="Board not found")
    return {"message": "Deleted successfully"}
