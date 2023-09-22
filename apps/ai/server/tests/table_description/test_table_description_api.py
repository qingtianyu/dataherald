from unittest import TestCase
from unittest.mock import AsyncMock, Mock, patch

from bson import ObjectId
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response

from app import app
from modules.db_connection.models.responses import DBConnectionResponse
from modules.organization.models.entities import Organization
from modules.user.models.entities import User

client = TestClient(app)


@patch("utils.auth.VerifyToken.verify", Mock(return_value={"email": ""}))
@patch.multiple(
    "utils.auth.Authorize",
    user=Mock(
        return_value=User(
            id="123",
            email="test@gmail.com",
            username="test_user",
            organization_id="123",
        )
    ),
    user_and_get_org_id=Mock(return_value="123"),
    get_organization_by_user=Mock(
        return_value=Organization(
            id="123", name="test_org", db_connection_id="0123456789ab0123456789ab"
        )
    ),
    table_description_in_organization=Mock(return_value=None),
)
class TestTableDescriptionAPI(TestCase):
    url = "/table-description"
    test_header = {"Authorization": "Bearer some-token"}
    test_1 = {
        "id": ObjectId(b"foo-bar-quux"),
        "table_name": "test_table",
        "description": "test_description",
        "columns": [
            {
                "categories": None,
                "data_type": None,
                "description": "test_description",
                "forengin_key": None,
                "is_primary_key": None,
                "low_cardinality": None,
                "name": "column1",
            }
        ],
        "examples": ["example1"],
    }

    test_response_0 = {
        "id": str(test_1["id"]),
        "table_name": test_1["table_name"],
        "description": test_1["description"],
        "columns": test_1["columns"],
        "examples": test_1["examples"],
    }

    test_response_1 = test_response_0.copy()

    test_db_response_1 = {
        "alias": "test_alias",
        "tables": [
            {
                "id": "666f6f2d6261722d71757578",
                "name": "test_table",
                "columns": ["column1"],
            }
        ],
    }

    @patch(
        "httpx.AsyncClient.get",
        AsyncMock(return_value=Response(status_code=200, json=[test_response_0])),
    )
    def test_get_table_descriptions(self):
        response = client.get(self.url + "/list", headers=self.test_header)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [self.test_response_1]

    @patch(
        "httpx.AsyncClient.get",
        AsyncMock(return_value=Response(status_code=200, json=[test_response_0])),
    )
    @patch(
        "modules.db_connection.service.DBConnectionService.get_db_connection",
        Mock(
            return_value=DBConnectionResponse(
                id="0123456789ab0123456789ab", alias=test_db_response_1["alias"]
            )
        ),
    )
    def test_get_database_table_descriptions(self):
        response = client.get(self.url + "/database/list", headers=self.test_header)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [self.test_db_response_1]

    @patch(
        "modules.table_description.service.TableDescriptionService.scan_table_descriptions",
        AsyncMock(return_value=True),
    )
    def test_scan_table_descriptions(self):
        response = client.post(
            self.url + "/scan",
            headers=self.test_header,
            json={"db_connection_id": "123", "table_names": ["test_table"]},
        )
        assert response.status_code == status.HTTP_201_CREATED

    @patch(
        "httpx.AsyncClient.patch",
        AsyncMock(return_value=Response(status_code=200, json=test_response_0)),
    )
    def test_update_table_description(self):
        response = client.patch(
            self.url + "/123",
            headers=self.test_header,
            json={
                "description": "test_description",
                "columns": [{"name": "column1", "description": "test_description"}],
                "examples": ["example1"],
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self.test_response_1
