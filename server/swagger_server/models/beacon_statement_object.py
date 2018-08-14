# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class BeaconStatementObject(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, id: str=None, name: str=None, category: str=None):  # noqa: E501
        """BeaconStatementObject - a model defined in Swagger

        :param id: The id of this BeaconStatementObject.  # noqa: E501
        :type id: str
        :param name: The name of this BeaconStatementObject.  # noqa: E501
        :type name: str
        :param category: The category of this BeaconStatementObject.  # noqa: E501
        :type category: str
        """
        self.swagger_types = {
            'id': str,
            'name': str,
            'category': str
        }

        self.attribute_map = {
            'id': 'id',
            'name': 'name',
            'category': 'category'
        }

        self._id = id
        self._name = name
        self._category = category

    @classmethod
    def from_dict(cls, dikt) -> 'BeaconStatementObject':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The BeaconStatementObject of this BeaconStatementObject.  # noqa: E501
        :rtype: BeaconStatementObject
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self) -> str:
        """Gets the id of this BeaconStatementObject.

        CURIE-encoded identifier of object concept   # noqa: E501

        :return: The id of this BeaconStatementObject.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id: str):
        """Sets the id of this BeaconStatementObject.

        CURIE-encoded identifier of object concept   # noqa: E501

        :param id: The id of this BeaconStatementObject.
        :type id: str
        """

        self._id = id

    @property
    def name(self) -> str:
        """Gets the name of this BeaconStatementObject.

        human readable label of object concept  # noqa: E501

        :return: The name of this BeaconStatementObject.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this BeaconStatementObject.

        human readable label of object concept  # noqa: E501

        :param name: The name of this BeaconStatementObject.
        :type name: str
        """

        self._name = name

    @property
    def category(self) -> str:
        """Gets the category of this BeaconStatementObject.

        a semantic group for the object concept (specified as a code gene, pathway, disease, etc. - see [Biolink Model](https://biolink.github.io/biolink-model) for the full list of categories)   # noqa: E501

        :return: The category of this BeaconStatementObject.
        :rtype: str
        """
        return self._category

    @category.setter
    def category(self, category: str):
        """Sets the category of this BeaconStatementObject.

        a semantic group for the object concept (specified as a code gene, pathway, disease, etc. - see [Biolink Model](https://biolink.github.io/biolink-model) for the full list of categories)   # noqa: E501

        :param category: The category of this BeaconStatementObject.
        :type category: str
        """

        self._category = category
