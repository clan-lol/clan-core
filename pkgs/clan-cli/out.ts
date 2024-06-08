export const schema = {
  "$comment": "An object containing API methods. ",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "open_file",
    "get_directory",
    "create_machine",
    "list_machines",
    "show_machine",
    "create_clan"
  ],
  "properties": {
    "open_file": {
      "type": "object",
      "required": [
        "arguments",
        "return"
      ],
      "additionalProperties": false,
      "properties": {
        "return": {
          "oneOf": [
            {
              "type": "object",
              "properties": {
                "status": {
                  "type": "string",
                  "enum": [
                    "success"
                  ],
                  "description": "The status of the response."
                },
                "data": {
                  "oneOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ]
                }
              },
              "required": [
                "status"
              ],
              "additionalProperties": false
            },
            {
              "type": "object",
              "properties": {
                "status": {
                  "type": "string",
                  "enum": [
                    "error"
                  ]
                },
                "errors": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "message": {
                        "type": "string"
                      },
                      "description": {
                        "oneOf": [
                          {
                            "type": "string"
                          },
                          {
                            "type": "null"
                          }
                        ]
                      },
                      "location": {
                        "oneOf": [
                          {
                            "type": "array",
                            "items": {
                              "type": "string"
                            }
                          },
                          {
                            "type": "null"
                          }
                        ]
                      }
                    },
                    "required": [
                      "message"
                    ],
                    "additionalProperties": false
                  }
                }
              },
              "required": [
                "status",
                "errors"
              ],
              "additionalProperties": false
            }
          ]
        },
        "arguments": {
          "type": "object",
          "required": [
            "file_request"
          ],
          "additionalProperties": false,
          "properties": {
            "file_request": {
              "type": "object",
              "properties": {
                "mode": {
                  "type": "string",
                  "enum": [
                    "open_file",
                    "select_folder"
                  ]
                },
                "title": {
                  "oneOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ]
                },
                "filters": {
                  "oneOf": [
                    {
                      "type": "object",
                      "properties": {
                        "title": {
                          "oneOf": [
                            {
                              "type": "string"
                            },
                            {
                              "type": "null"
                            }
                          ]
                        },
                        "mime_types": {
                          "oneOf": [
                            {
                              "type": "array",
                              "items": {
                                "type": "string"
                              }
                            },
                            {
                              "type": "null"
                            }
                          ]
                        },
                        "patterns": {
                          "oneOf": [
                            {
                              "type": "array",
                              "items": {
                                "type": "string"
                              }
                            },
                            {
                              "type": "null"
                            }
                          ]
                        },
                        "suffixes": {
                          "oneOf": [
                            {
                              "type": "array",
                              "items": {
                                "type": "string"
                              }
                            },
                            {
                              "type": "null"
                            }
                          ]
                        }
                      },
                      "required": [],
                      "additionalProperties": false
                    },
                    {
                      "type": "null"
                    }
                  ]
                }
              },
              "required": [
                "mode"
              ],
              "additionalProperties": false
            }
          }
        }
      }
    },
    "get_directory": {
      "type": "object",
      "required": [
        "arguments",
        "return"
      ],
      "additionalProperties": false,
      "properties": {
        "return": {
          "oneOf": [
            {
              "type": "object",
              "properties": {
                "status": {
                  "type": "string",
                  "enum": [
                    "success"
                  ],
                  "description": "The status of the response."
                },
                "data": {
                  "type": "object",
                  "properties": {
                    "path": {
                      "type": "string"
                    },
                    "files": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "path": {
                            "type": "string"
                          },
                          "file_type": {
                            "type": "string",
                            "enum": [
                              "file",
                              "directory",
                              "symlink"
                            ]
                          }
                        },
                        "required": [
                          "path",
                          "file_type"
                        ],
                        "additionalProperties": false
                      }
                    }
                  },
                  "required": [
                    "path",
                    "files"
                  ],
                  "additionalProperties": false
                }
              },
              "required": [
                "status",
                "data"
              ],
              "additionalProperties": false
            },
            {
              "type": "object",
              "properties": {
                "status": {
                  "type": "string",
                  "enum": [
                    "error"
                  ]
                },
                "errors": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "message": {
                        "type": "string"
                      },
                      "description": {
                        "oneOf": [
                          {
                            "type": "string"
                          },
                          {
                            "type": "null"
                          }
                        ]
                      },
                      "location": {
                        "oneOf": [
                          {
                            "type": "array",
                            "items": {
                              "type": "string"
                            }
                          },
                          {
                            "type": "null"
                          }
                        ]
                      }
                    },
                    "required": [
                      "message"
                    ],
                    "additionalProperties": false
                  }
                }
              },
              "required": [
                "status",
                "errors"
              ],
              "additionalProperties": false
            }
          ]
        },
        "arguments": {
          "type": "object",
          "required": [
            "current_path"
          ],
          "additionalProperties": false,
          "properties": {
            "current_path": {
              "type": "string"
            }
          }
        }
      }
    },
    "create_machine": {
      "type": "object",
      "required": [
        "arguments",
        "return"
      ],
      "additionalProperties": false,
      "properties": {
        "return": {
          "oneOf": [
            {
              "type": "object",
              "properties": {
                "status": {
                  "type": "string",
                  "enum": [
                    "success"
                  ],
                  "description": "The status of the response."
                },
                "data": {
                  "type": "null"
                }
              },
              "required": [
                "status"
              ],
              "additionalProperties": false
            },
            {
              "type": "object",
              "properties": {
                "status": {
                  "type": "string",
                  "enum": [
                    "error"
                  ]
                },
                "errors": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "message": {
                        "type": "string"
                      },
                      "description": {
                        "oneOf": [
                          {
                            "type": "string"
                          },
                          {
                            "type": "null"
                          }
                        ]
                      },
                      "location": {
                        "oneOf": [
                          {
                            "type": "array",
                            "items": {
                              "type": "string"
                            }
                          },
                          {
                            "type": "null"
                          }
                        ]
                      }
                    },
                    "required": [
                      "message"
                    ],
                    "additionalProperties": false
                  }
                }
              },
              "required": [
                "status",
                "errors"
              ],
              "additionalProperties": false
            }
          ]
        },
        "arguments": {
          "type": "object",
          "required": [
            "flake_dir",
            "machine"
          ],
          "additionalProperties": false,
          "properties": {
            "flake_dir": {
              "oneOf": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            },
            "machine": {
              "type": "object",
              "properties": {
                "name": {
                  "type": "string"
                },
                "config": {
                  "type": "object",
                  "additionalProperties": {
                    "type": "integer"
                  }
                }
              },
              "required": [
                "name",
                "config"
              ],
              "additionalProperties": false
            }
          }
        }
      }
    },
    "list_machines": {
      "type": "object",
      "required": [
        "arguments",
        "return"
      ],
      "additionalProperties": false,
      "properties": {
        "return": {
          "oneOf": [
            {
              "type": "object",
              "properties": {
                "status": {
                  "type": "string",
                  "enum": [
                    "success"
                  ],
                  "description": "The status of the response."
                },
                "data": {
                  "type": "array",
                  "items": {
                    "type": "string"
                  }
                }
              },
              "required": [
                "status",
                "data"
              ],
              "additionalProperties": false
            },
            {
              "type": "object",
              "properties": {
                "status": {
                  "type": "string",
                  "enum": [
                    "error"
                  ]
                },
                "errors": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "message": {
                        "type": "string"
                      },
                      "description": {
                        "oneOf": [
                          {
                            "type": "string"
                          },
                          {
                            "type": "null"
                          }
                        ]
                      },
                      "location": {
                        "oneOf": [
                          {
                            "type": "array",
                            "items": {
                              "type": "string"
                            }
                          },
                          {
                            "type": "null"
                          }
                        ]
                      }
                    },
                    "required": [
                      "message"
                    ],
                    "additionalProperties": false
                  }
                }
              },
              "required": [
                "status",
                "errors"
              ],
              "additionalProperties": false
            }
          ]
        },
        "arguments": {
          "type": "object",
          "required": [
            "flake_url",
            "debug"
          ],
          "additionalProperties": false,
          "properties": {
            "flake_url": {
              "oneOf": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            },
            "debug": {
              "type": "boolean"
            }
          }
        }
      }
    },
    "show_machine": {
      "type": "object",
      "required": [
        "arguments",
        "return"
      ],
      "additionalProperties": false,
      "properties": {
        "return": {
          "oneOf": [
            {
              "type": "object",
              "properties": {
                "status": {
                  "type": "string",
                  "enum": [
                    "success"
                  ],
                  "description": "The status of the response."
                },
                "data": {
                  "type": "object",
                  "properties": {
                    "machine_name": {
                      "type": "string"
                    },
                    "machine_description": {
                      "oneOf": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "null"
                        }
                      ]
                    },
                    "machine_icon": {
                      "oneOf": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "null"
                        }
                      ]
                    }
                  },
                  "required": [
                    "machine_name"
                  ],
                  "additionalProperties": false
                }
              },
              "required": [
                "status",
                "data"
              ],
              "additionalProperties": false
            },
            {
              "type": "object",
              "properties": {
                "status": {
                  "type": "string",
                  "enum": [
                    "error"
                  ]
                },
                "errors": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "message": {
                        "type": "string"
                      },
                      "description": {
                        "oneOf": [
                          {
                            "type": "string"
                          },
                          {
                            "type": "null"
                          }
                        ]
                      },
                      "location": {
                        "oneOf": [
                          {
                            "type": "array",
                            "items": {
                              "type": "string"
                            }
                          },
                          {
                            "type": "null"
                          }
                        ]
                      }
                    },
                    "required": [
                      "message"
                    ],
                    "additionalProperties": false
                  }
                }
              },
              "required": [
                "status",
                "errors"
              ],
              "additionalProperties": false
            }
          ]
        },
        "arguments": {
          "type": "object",
          "required": [
            "flake_url",
            "machine_name",
            "debug"
          ],
          "additionalProperties": false,
          "properties": {
            "flake_url": {
              "oneOf": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            },
            "machine_name": {
              "type": "string"
            },
            "debug": {
              "type": "boolean"
            }
          }
        }
      }
    },
    "create_clan": {
      "type": "object",
      "required": [
        "arguments",
        "return"
      ],
      "additionalProperties": false,
      "properties": {
        "return": {
          "oneOf": [
            {
              "type": "object",
              "properties": {
                "status": {
                  "type": "string",
                  "enum": [
                    "success"
                  ],
                  "description": "The status of the response."
                },
                "data": {
                  "type": "object",
                  "properties": {
                    "git_init": {
                      "type": "object",
                      "properties": {
                        "stdout": {
                          "type": "string"
                        },
                        "stderr": {
                          "type": "string"
                        },
                        "cwd": {
                          "type": "string"
                        },
                        "command": {
                          "type": "string"
                        },
                        "returncode": {
                          "type": "integer"
                        },
                        "msg": {
                          "oneOf": [
                            {
                              "type": "string"
                            },
                            {
                              "type": "null"
                            }
                          ]
                        }
                      },
                      "required": [
                        "stdout",
                        "stderr",
                        "cwd",
                        "command",
                        "returncode"
                      ],
                      "additionalProperties": false
                    },
                    "git_add": {
                      "type": "object",
                      "properties": {
                        "stdout": {
                          "type": "string"
                        },
                        "stderr": {
                          "type": "string"
                        },
                        "cwd": {
                          "type": "string"
                        },
                        "command": {
                          "type": "string"
                        },
                        "returncode": {
                          "type": "integer"
                        },
                        "msg": {
                          "oneOf": [
                            {
                              "type": "string"
                            },
                            {
                              "type": "null"
                            }
                          ]
                        }
                      },
                      "required": [
                        "stdout",
                        "stderr",
                        "cwd",
                        "command",
                        "returncode"
                      ],
                      "additionalProperties": false
                    },
                    "git_config": {
                      "type": "object",
                      "properties": {
                        "stdout": {
                          "type": "string"
                        },
                        "stderr": {
                          "type": "string"
                        },
                        "cwd": {
                          "type": "string"
                        },
                        "command": {
                          "type": "string"
                        },
                        "returncode": {
                          "type": "integer"
                        },
                        "msg": {
                          "oneOf": [
                            {
                              "type": "string"
                            },
                            {
                              "type": "null"
                            }
                          ]
                        }
                      },
                      "required": [
                        "stdout",
                        "stderr",
                        "cwd",
                        "command",
                        "returncode"
                      ],
                      "additionalProperties": false
                    },
                    "flake_update": {
                      "type": "object",
                      "properties": {
                        "stdout": {
                          "type": "string"
                        },
                        "stderr": {
                          "type": "string"
                        },
                        "cwd": {
                          "type": "string"
                        },
                        "command": {
                          "type": "string"
                        },
                        "returncode": {
                          "type": "integer"
                        },
                        "msg": {
                          "oneOf": [
                            {
                              "type": "string"
                            },
                            {
                              "type": "null"
                            }
                          ]
                        }
                      },
                      "required": [
                        "stdout",
                        "stderr",
                        "cwd",
                        "command",
                        "returncode"
                      ],
                      "additionalProperties": false
                    }
                  },
                  "required": [
                    "git_init",
                    "git_add",
                    "git_config",
                    "flake_update"
                  ],
                  "additionalProperties": false
                }
              },
              "required": [
                "status",
                "data"
              ],
              "additionalProperties": false
            },
            {
              "type": "object",
              "properties": {
                "status": {
                  "type": "string",
                  "enum": [
                    "error"
                  ]
                },
                "errors": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "message": {
                        "type": "string"
                      },
                      "description": {
                        "oneOf": [
                          {
                            "type": "string"
                          },
                          {
                            "type": "null"
                          }
                        ]
                      },
                      "location": {
                        "oneOf": [
                          {
                            "type": "array",
                            "items": {
                              "type": "string"
                            }
                          },
                          {
                            "type": "null"
                          }
                        ]
                      }
                    },
                    "required": [
                      "message"
                    ],
                    "additionalProperties": false
                  }
                }
              },
              "required": [
                "status",
                "errors"
              ],
              "additionalProperties": false
            }
          ]
        },
        "arguments": {
          "type": "object",
          "required": [
            "directory",
            "template_url"
          ],
          "additionalProperties": false,
          "properties": {
            "directory": {
              "type": "string"
            },
            "template_url": {
              "type": "string"
            }
          }
        }
      }
    }
  }
} as const;

