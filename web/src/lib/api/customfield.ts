/**
 * 自定义字段API客户端模块
 *
 * 本模块提供与后端自定义字段功能相关的所有API调用函数和类型定义。
 * 包括JSON Schema的管理（创建、更新、删除、查询等）和自定义字段值的操作。
 * 同时提供基于SWR的React Hooks，便于React组件中使用。
 *
 * 自定义字段功能包含两个主要概念：
 * 1. JSON Schema：定义字段结构、验证规则和UI展示方式
 * 2. JSON Value：实体的具体自定义字段值数据
 *
 * @module customfield
 */
import { PageParams, PageResult } from "@/lib/types";
import { serverAPI, ApiResponse } from "./client";
import useSWR from "swr";

// API前缀
const API_PREFIX = "customfield";

/**
 * JSON Schema定义接口
 *
 * 表示一个完整的JSON Schema，包含结构定义和元数据信息
 */
export interface JsonSchemaSchema {
  /** Schema唯一标识ID */
  id: number;
  /** Schema名称 */
  name: string;
  /** 适用的实体类型，如"Employee"、"Company"等 */
  entity_type: string;
  /** JSON Schema定义，遵循JSON Schema规范 */
  schema_value: Record<string, any>;
  /** UI展示相关配置，可选，用于指导前端如何渲染表单 */
  ui_schema?: Record<string, any> | null;
  /** 关联的公司ID，null表示系统级Schema */
  company_id?: number | null;
  /** 是否为系统预设Schema，系统Schema只能由超级管理员修改 */
  is_system: boolean;
  /** Schema版本号，每次结构变更会增加 */
  version: number;
  /** 父Schema ID，用于版本管理，指向旧版本 */
  parent_schema_id?: number | null;
  /** 备注信息 */
  remark?: string | null;
  /** 创建时间 */
  created_at?: string | null;
  /** 最后更新时间 */
  updated_at?: string | null;
}

/**
 * 创建JSON Schema接口
 *
 * 用于创建新Schema的请求参数
 */
export interface JsonSchemaCreate {
  /** Schema名称 */
  name: string;
  /** 适用的实体类型，如"Employee"、"Company"等 */
  entity_type: string;
  /** JSON Schema定义，遵循JSON Schema规范 */
  schema_value: Record<string, any>; // 修改处
  /** UI展示相关配置，可选 */
  ui_schema?: Record<string, any>;
  /** 关联的公司ID，可选，不提供则为系统级Schema */
  company_id?: number;
  /** 是否为系统预设Schema，默认为false */
  is_system?: boolean;
  /** 备注信息 */
  remark?: string;
}

/**
 * 更新JSON Schema接口
 *
 * 用于更新现有Schema的请求参数，所有字段均为可选
 */
export interface JsonSchemaUpdate {
  /** Schema名称，可选 */
  name?: string;
  /** JSON Schema定义，可选，更新此字段会创建新版本 */
  schema_value?: Record<string, any>; // 修改处
  /** UI展示相关配置，可选 */
  ui_schema?: Record<string, any>;
  /** 备注信息，可选 */
  remark?: string;
}

/**
 * 克隆JSON Schema接口
 *
 * 用于克隆Schema到另一个公司的请求参数
 */
export interface JsonSchemaClone {
  /** 源Schema ID */
  source_schema_id: number;
  /** 目标公司ID */
  target_company_id: number;
  /** 新Schema名称，可选，默认使用源Schema名称 */
  name?: string;
}

/**
 * JSON值接口
 *
 * 表示一个实体的自定义字段值数据
 */
export interface JsonValueSchema {
  /** 值唯一标识ID */
  id: number;
  /** 关联的Schema ID */
  schema_id: number;
  /** 关联的实体ID，如员工ID、公司ID等 */
  entity_id: number;
  /** 关联的实体类型，如"employee"、"company"等 */
  entity_type: string;
  /** JSON格式的数据值，结构由关联的Schema决定 */
  value: Record<string, any>;
  /** 备注信息 */
  remark?: string;
  /** 创建时间 */
  created_at?: string | null;
  /** 最后更新时间 */
  updated_at?: string | null;
}

/**
 * 创建JSON值接口
 *
 * 用于创建新的自定义字段值的请求参数
 */
export interface JsonValueCreate {
  /** 关联的Schema ID */
  schema_id: number;
  /** 关联的实体ID，如员工ID、公司ID等 */
  entity_id: number;
  /** 关联的实体类型，如"employee"、"company"等 */
  entity_type: string;
  /** JSON格式的数据值，结构由关联的Schema决定 */
  value: Record<string, any>;
  /** 备注信息，可选 */
  remark?: string;
}

/**
 * 更新JSON值接口
 *
 * 用于更新现有的自定义字段值的请求参数
 */
export interface JsonValueUpdate {
  /** JSON格式的数据值，结构由关联的Schema决定 */
  value: Record<string, any>;
  /** 备注信息，可选 */
  remark?: string;
}

/**
 * 获取JSON Schema列表
 *
 * 按实体类型获取Schema列表，支持分页、公司筛选和是否包含系统Schema的选项。
 *
 * @param entityType 实体类型，如"Employee"、"Company"等
 * @param params 分页参数，包含page和limit
 * @param companyId 可选，指定公司ID，筛选该公司的Schema
 * @param includeSystem 是否包含系统Schema，默认为true
 * @returns 包含Schema列表和分页信息的Promise
 * @throws 请求失败时抛出错误
 */
export async function getSchemaList(
  entityType: string,
  params: PageParams,
  companyId?: number,
  includeSystem: boolean = true
): Promise<PageResult<JsonSchemaSchema>> {
  const searchParams: Record<string, string> = {
    page: params.page.toString(),
    limit: params.limit.toString(),
    include_system: includeSystem.toString(),
  };

  if (companyId !== undefined) {
    searchParams.company_id = companyId.toString();
  }

  const response = await serverAPI
    .get(`${API_PREFIX}/schema/list/${entityType}`, {
      searchParams,
    })
    .json<ApiResponse<PageResult<JsonSchemaSchema>>>();

  if (!response.data) throw new Error("No data returned");
  return response.data;
}

/**
 * 获取JSON Schema详情
 *
 * 通过ID获取单个Schema的完整信息。
 *
 * @param id Schema ID
 * @returns Schema详情的Promise
 * @throws Schema不存在或无权限时抛出错误
 */
export async function getSchemaById(id: number): Promise<JsonSchemaSchema> {
  const response = await serverAPI
    .get(`${API_PREFIX}/schema/get/${id}`)
    .json<ApiResponse<JsonSchemaSchema>>();

  if (!response.data) throw new Error("No data returned");
  return response.data;
}

/**
 * 创建JSON Schema
 *
 * 创建一个新的JSON Schema定义，用于自定义字段。
 *
 * @param data 创建Schema的数据，包含名称、实体类型、结构定义等
 * @returns 创建成功后的Schema信息Promise
 * @throws 权限不足或创建失败时抛出错误
 */
export async function createJsonSchema(
  data: JsonSchemaCreate
): Promise<JsonSchemaSchema> {
  const response = await serverAPI
    .post(`${API_PREFIX}/schema/create`, {
      json: data,
    })
    .json<ApiResponse<JsonSchemaSchema>>();

  if (!response.data) throw new Error("No data returned");
  return response.data;
}

/**
 * 更新JSON Schema
 *
 * 更新现有的JSON Schema定义。如果更新涉及Schema的结构变化，
 * 会创建新版本的Schema并保留对旧版本的引用。
 *
 * @param id 要更新的Schema ID
 * @param data 更新数据，包含可选的名称、结构、UI配置等
 * @returns 更新后的Schema信息Promise
 * @throws Schema不存在、权限不足或更新失败时抛出错误
 */
export async function updateJsonSchema(
  id: number,
  data: JsonSchemaUpdate
): Promise<JsonSchemaSchema> {
  const response = await serverAPI
    .post(`${API_PREFIX}/schema/update/${id}`, {
      json: data,
    })
    .json<ApiResponse<JsonSchemaSchema>>();

  if (!response.data) throw new Error("No data returned");
  return response.data;
}

/**
 * 删除JSON Schema
 *
 * 删除现有的JSON Schema定义。只有当没有数据使用该Schema时才能删除。
 * 系统预设的Schema只能由超级管理员删除。
 *
 * @param id 要删除的Schema ID
 * @returns 无返回值的Promise
 * @throws Schema不存在、已有关联数据或权限不足时抛出错误
 */
export async function deleteJsonSchema(id: number): Promise<void> {
  await serverAPI
    .post(`${API_PREFIX}/schema/delete/${id}`)
    .json<ApiResponse<void>>();
}

/**
 * 克隆JSON Schema
 *
 * 将现有的JSON Schema克隆到另一个公司。新创建的Schema是独立的副本，
 * 不会受源Schema后续变更的影响。
 *
 * @param data 克隆参数，包含源SchemaID、目标公司ID和可选的新名称
 * @returns 克隆后的新Schema信息Promise
 * @throws 源Schema不存在、目标公司不存在或权限不足时抛出错误
 */
export async function cloneJsonSchema(
  data: JsonSchemaClone
): Promise<JsonSchemaSchema> {
  const response = await serverAPI
    .post(`${API_PREFIX}/schema/clone`, {
      json: data,
    })
    .json<ApiResponse<JsonSchemaSchema>>();

  if (!response.data) throw new Error("No data returned");
  return response.data;
}

/**
 * 获取实体的自定义字段值
 *
 * 获取指定实体的所有自定义字段值，或者筛选特定Schema的值。
 *
 * @param entityType 实体类型，如"employee"、"company"等
 * @param entityId 实体ID
 * @param schemaId 可选，指定Schema ID，只返回该Schema的值
 * @returns 实体的自定义字段值数组Promise
 * @throws 实体不存在或权限不足时抛出错误
 */
export async function getEntityValues(
  entityType: string,
  entityId: number,
  schemaId?: number
): Promise<JsonValueSchema[]> {
  const searchParams: Record<string, string> = {};
  if (schemaId !== undefined) {
    searchParams.schema_id = schemaId.toString();
  }

  const response = await serverAPI
    .get(`${API_PREFIX}/value/entity/${entityType}/${entityId}`, {
      searchParams,
    })
    .json<ApiResponse<JsonValueSchema[]>>();

  if (!response.data) throw new Error("No data returned");
  return response.data;
}

/**
 * 创建自定义字段值
 *
 * 为实体创建自定义字段值。系统会根据关联的Schema验证提交的数据。
 *
 * @param data 创建值的数据，包含SchemaID、实体信息和值数据
 * @returns 创建成功后的值信息Promise
 * @throws 数据验证失败、Schema不存在或权限不足时抛出错误
 */
export async function createJsonValue(
  data: JsonValueCreate
): Promise<JsonValueSchema> {
  const response = await serverAPI
    .post(`${API_PREFIX}/value/create`, {
      json: data,
    })
    .json<ApiResponse<JsonValueSchema>>();

  if (!response.data) throw new Error("No data returned");
  return response.data;
}

/**
 * 更新自定义字段值
 *
 * 更新实体的自定义字段值。系统会根据关联的Schema验证更新后的数据。
 *
 * @param id 值ID
 * @param data 更新数据，包含值数据和可选的备注
 * @returns 更新后的值信息Promise
 * @throws 数据验证失败、值不存在或权限不足时抛出错误
 */
export async function updateJsonValue(
  id: number,
  data: JsonValueUpdate
): Promise<JsonValueSchema> {
  const response = await serverAPI
    .post(`${API_PREFIX}/value/update/${id}`, {
      json: data,
    })
    .json<ApiResponse<JsonValueSchema>>();

  if (!response.data) throw new Error("No data returned");
  return response.data;
}

/**
 * 删除自定义字段值
 *
 * 删除实体的自定义字段值。这将永久删除该数据，不可恢复。
 *
 * @param id 要删除的值ID
 * @returns 无返回值的Promise
 * @throws 值不存在或权限不足时抛出错误
 */
export async function deleteJsonValue(id: number): Promise<void> {
  await serverAPI
    .post(`${API_PREFIX}/value/delete/${id}`)
    .json<ApiResponse<void>>();
}

// SWR Hooks

/**
 * 使用SWR获取Schema列表
 *
 * 基于SWR的Hook，用于在React组件中获取和缓存JSON Schema列表。
 * 支持SWR的自动重新验证和错误处理特性。
 *
 * @param entityType 实体类型，如"Employee"、"Company"等
 * @param params 分页参数
 * @param companyId 可选，指定公司ID
 * @param includeSystem 是否包含系统Schema，默认为true
 * @returns SWR响应对象，包含data、error、isLoading等属性
 * @example
 * ```tsx
 * const { data, error, isLoading } = useSchemaList('Company', { page: 1, limit: 10 });
 * ```
 */
export function useSchemaList(
  entityType: string,
  params: PageParams,
  companyId?: number,
  includeSystem: boolean = true
) {
  return useSWR(
    [`${API_PREFIX}/schema/list`, entityType, params, companyId, includeSystem],
    async () =>
      await getSchemaList(entityType, params, companyId, includeSystem)
  );
}

/**
 * 使用SWR获取Schema详情
 *
 * 基于SWR的Hook，用于在React组件中获取和缓存单个JSON Schema的详情。
 * 当id为undefined时不会触发请求。
 *
 * @param id Schema ID，可选
 * @returns SWR响应对象，包含data、error、isLoading等属性
 * @example
 * ```tsx
 * const { data, error, isLoading } = useSchema(schemaId);
 * ```
 */
export function useSchema(id: number | undefined) {
  return useSWR(id ? [`${API_PREFIX}/schema`, id] : null, async () => {
    if (!id) return null;
    return await getSchemaById(id);
  });
}

/**
 * 使用SWR获取实体的自定义字段值
 *
 * 基于SWR的Hook，用于在React组件中获取和缓存实体的自定义字段值。
 * 当entityType或entityId为undefined时不会触发请求。
 *
 * @param entityType 实体类型，如"employee"、"company"等
 * @param entityId 实体ID
 * @param schemaId 可选，指定Schema ID，只返回该Schema的值
 * @returns SWR响应对象，包含data、error、isLoading等属性
 * @example
 * ```tsx
 * const { data, error, isLoading } = useEntityValues('company', companyId);
 * ```
 */
export function useEntityValues(
  entityType: string | undefined,
  entityId: number | undefined,
  schemaId?: number
) {
  return useSWR(
    entityType && entityId
      ? [`${API_PREFIX}/values`, entityType, entityId, schemaId]
      : null,
    async () => {
      if (!entityType || !entityId) return null;
      return await getEntityValues(entityType, entityId, schemaId);
    }
  );
}
