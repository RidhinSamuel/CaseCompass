import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { RootState } from '../app/store';

export interface Document {
  id: string;
  user_id: string;
  case_id?: string | null;
  title: string;
  status: string;
  chunk_count: number;
  created_at: string;
}

export interface SearchHit {
  chunk_id: string;
  document_id: string;
<<<<<<< HEAD
  document_title: str;
=======
  document_title: string;
>>>>>>> bb82cedc2e563d85a6f093172bb4135cbe364134
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

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token;
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['Document', 'User'],
  endpoints: (builder) => ({
    registerUser: builder.mutation({
      query: (userData) => ({
        url: '/auth/register',
        method: 'POST',
        body: userData,
      }),
    }),
    loginUser: builder.mutation({
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
    getMe: builder.query({
      query: () => '/auth/me',
      providesTags: ['User'],
    }),
    getDocuments: builder.query<Document[], void>({
      query: () => '/documents',
      providesTags: ['Document'],
    }),
    createDocument: builder.mutation({
      query: (docData) => ({
        url: '/documents',
        method: 'POST',
        body: docData,
      }),
      invalidatesTags: ['Document'],
    }),
    searchCases: builder.mutation<SearchResponse, { query: string; case_id?: string; top_k?: number }>({
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
  useSearchCasesMutation,
} = apiSlice;
