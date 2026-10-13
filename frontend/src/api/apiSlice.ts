import {
  createApi,
  fetchBaseQuery,
  type BaseQueryFn,
  type FetchArgs,
  type FetchBaseQueryError,
} from '@reduxjs/toolkit/query/react';
import type { RootState } from '../app/store';
import { logout, type User } from '../features/authSlice';

export interface Document {
  id: string;
  user_id: string;
  case_id?: string | null;
  title: string;
  source_filename?: string | null;
  status: string;
  chunk_count: number;
  created_at: string;
}

export interface SearchHit {
  chunk_id: string;
  document_id: string;
  document_title: string;
  content: string;
  score: number;
  case_id?: string | null;
  chunk_index: number;
}

export interface SearchResponse {
  query: string;
  answer: string;
  hits: SearchHit[];
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface CreateDocumentRequest {
  title: string;
  raw_text: string;
  case_id?: string;
  metadata?: Record<string, unknown>;
}

export interface SearchRequest {
  query: string;
  case_id?: string;
  top_k?: number;
}

// API base URL: same-origin "/api" by default (nginx / Vite proxy forward it).
// Set VITE_API_BASE_URL at build time when the API lives on another domain.
// `||` (not `??`): the Docker build passes an empty string when the arg is unset.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const rawBaseQuery = fetchBaseQuery({
  baseUrl: API_BASE_URL,
  prepareHeaders: (headers, { getState }) => {
    const token = (getState() as RootState).auth.token;
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
    return headers;
  },
});

// Log the user out when the token is expired or invalid, instead of
// leaving them on a page where every request fails.
const baseQueryWithAuth: BaseQueryFn<string | FetchArgs, unknown, FetchBaseQueryError> = async (
  args,
  api,
  extraOptions,
) => {
  const result = await rawBaseQuery(args, api, extraOptions);
  if (result.error?.status === 401 && (api.getState() as RootState).auth.token) {
    api.dispatch(logout());
  }
  return result;
};

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithAuth,
  tagTypes: ['Document', 'User'],
  endpoints: (builder) => ({
    registerUser: builder.mutation<User, RegisterRequest>({
      query: (userData) => ({
        url: '/auth/register',
        method: 'POST',
        body: userData,
      }),
    }),
    loginUser: builder.mutation<TokenResponse, LoginRequest>({
      query: (credentials) => {
        const formData = new URLSearchParams();
        formData.append('username', credentials.email);
        formData.append('password', credentials.password);
        return {
          url: '/auth/login',
          method: 'POST',
          body: formData,
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        };
      },
    }),
    getMe: builder.query<User, void>({
      query: () => '/auth/me',
      providesTags: ['User'],
    }),
    getDocuments: builder.query<Document[], void>({
      query: () => '/documents',
      providesTags: ['Document'],
    }),
    createDocument: builder.mutation<Document, CreateDocumentRequest>({
      query: (docData) => ({
        url: '/documents',
        method: 'POST',
        body: docData,
      }),
      invalidatesTags: ['Document'],
    }),
    uploadDocument: builder.mutation<Document, FormData>({
      // No Content-Type header: the browser adds the multipart boundary.
      query: (formData) => ({
        url: '/documents/upload',
        method: 'POST',
        body: formData,
      }),
      invalidatesTags: ['Document'],
    }),
    deleteDocument: builder.mutation<void, string>({
      query: (id) => ({ url: `/documents/${id}`, method: 'DELETE' }),
      invalidatesTags: ['Document'],
    }),
    retryDocument: builder.mutation<Document, string>({
      query: (id) => ({ url: `/documents/${id}/retry`, method: 'POST' }),
      invalidatesTags: ['Document'],
    }),
    searchCases: builder.mutation<SearchResponse, SearchRequest>({
      query: (searchParams) => ({
        url: '/search',
        method: 'POST',
        body: searchParams,
      }),
    }),
  }),
});

export const {
  useRegisterUserMutation,
  useLoginUserMutation,
  useGetMeQuery,
  useGetDocumentsQuery,
  useCreateDocumentMutation,
  useUploadDocumentMutation,
  useDeleteDocumentMutation,
  useRetryDocumentMutation,
  useSearchCasesMutation,
} = apiSlice;
